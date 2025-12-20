from fastapi import FastAPI

app = FastAPI(title="Credit Scoring API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


