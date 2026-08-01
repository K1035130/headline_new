from fastapi import FastAPI
from routers import news, users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Headline Backend")

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