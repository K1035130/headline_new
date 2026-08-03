import json

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import ai_conf
from config.db_conf import async_session, get_db
from crud import ai_chat
from models.users import User
from schemas.ai_chat import ChatHistoryData, ChatHistoryItemOut, ChatRequest
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/ai", tags=["ai"])

REQUEST_TIMEOUT = httpx.Timeout(120.0, connect=10.0)


def sse_error(message: str, code: str = "error") -> str:
    """Deliver a failure through the stream the client is already reading.

    `code` lets the frontend show a localized message; `message` is the
    English fallback for anything it doesn't recognise.
    """
    payload = {"error": {"message": message, "code": code}}
    return f"data: {json.dumps(payload)}\n\n"


def describe_upstream_error(status_code: int) -> tuple[str, str]:
    """Turn an upstream status into (message, code) worth showing a user."""
    if status_code == 429:
        return (
            "Rate limit reached. The free tier allows 5 requests per minute "
            "and 20 per day — please wait and try again.",
            "rate_limit",
        )
    if status_code in (401, 403):
        return ("The AI service rejected the request.", "auth_failed")
    if status_code == 404:
        return ("The configured AI model is unavailable.", "model_unavailable")
    return (f"AI request failed ({status_code}).", "upstream_error")


@router.post("/chat")
async def chat(payload: ChatRequest, user: User = Depends(get_current_user)):
    if not ai_conf.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured",
        )

    question = next(
        (m.content for m in reversed(payload.messages) if m.role == "user"), ""
    )

    async def event_stream():
        answer_parts: list[str] = []

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    ai_conf.CHAT_COMPLETIONS_URL,
                    headers={
                        "Authorization": f"Bearer {ai_conf.GEMINI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": ai_conf.GEMINI_MODEL,
                        "messages": [m.model_dump() for m in payload.messages],
                        "stream": True,
                    },
                ) as upstream:
                    if upstream.status_code != 200:
                        body = (await upstream.aread()).decode("utf-8", "replace")
                        # full details stay in the server log; the client gets a
                        # summary so nothing about the key or quota leaks out
                        print(f"[ai] upstream {upstream.status_code}: {body[:500]}")
                        message, code = describe_upstream_error(upstream.status_code)
                        yield sse_error(message, code)
                        return

                    async for line in upstream.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:].strip()
                            if data and data != "[DONE]":
                                try:
                                    chunk = json.loads(data)
                                    delta = (
                                        chunk.get("choices", [{}])[0]
                                        .get("delta", {})
                                        .get("content")
                                    )
                                    if delta:
                                        answer_parts.append(delta)
                                except (json.JSONDecodeError, IndexError, AttributeError):
                                    pass
                        # forwarded verbatim so the existing frontend parser works
                        yield f"{line}\n"

        except httpx.TimeoutException as exc:
            print(f"[ai] timeout: {exc}")
            yield sse_error("The AI service took too long to respond.", "timeout")
            return
        except httpx.HTTPError as exc:
            print(f"[ai] transport error: {exc}")
            yield sse_error("Could not reach the AI service.", "unreachable")
            return
        except Exception as exc:  # noqa: BLE001 - a crash here would hang the stream
            print(f"[ai] unexpected error: {type(exc).__name__}: {exc}")
            yield sse_error("Something went wrong while answering.", "internal_error")
            return

        answer = "".join(answer_parts)
        if question and answer:
            try:
                # a separate session: the request-scoped one may already be
                # closed by the time the stream finishes
                async with async_session() as session:
                    await ai_chat.save_exchange(
                        session, user_id=user.id, question=question, answer=answer
                    )
                    await session.commit()
            except Exception as exc:  # noqa: BLE001
                # the user already has their answer — losing the log is not
                # worth failing the response over
                print(f"[ai] failed to save exchange: {type(exc).__name__}: {exc}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/history")
async def get_chat_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    messages, total = await ai_chat.get_chat_history(db, user_id=user.id)

    return success_response(
        data=ChatHistoryData(
            list=[ChatHistoryItemOut.model_validate(m) for m in messages],
            total=total,
        )
    )


@router.delete("/history")
async def clear_chat_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    removed = await ai_chat.clear_chat_history(db, user_id=user.id)

    return success_response(message=f"Cleared {removed} message(s)")
