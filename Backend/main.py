from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routers import news, users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Headline Backend")


# Errors are returned in the same {code, message, data} envelope the endpoints
# use, so the frontend can read `message` off both success and failure paths.
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = "; ".join(
        f"{'.'.join(str(part) for part in err['loc'][1:])}: {err['msg']}"
        for err in exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": message or "Invalid request", "data": None},
    )


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