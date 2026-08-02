from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from routers import favorite, news, users
from fastapi.middleware.cors import CORSMiddleware

from utils.response import error_response

app = FastAPI(title="Headline Backend")


# Errors go through the same envelope helper as successful responses, so the
# frontend can read `message` off both paths.
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(exc.status_code, exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = "; ".join(
        f"{'.'.join(str(part) for part in err['loc'][1:])}: {err['msg']}"
        for err in exc.errors()
    )
    return error_response(422, message or "Invalid request")


@app.get("/health")
def health():
    return {"status": "ok"}


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the news router
app.include_router(news.router)
# Include the users router
app.include_router(users.router)
# Include the favorite router
app.include_router(favorite.router)