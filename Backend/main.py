from fastapi import FastAPI

app = FastAPI(title="Headline Backend")


@app.get("/health")
def health():
    return {"status": "ok"}
