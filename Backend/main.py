from fastapi import FastAPI
from routers import news, users

app = FastAPI(title="Headline Backend")

app.include_router(news.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Include the news router
app.include_router(news.router)
