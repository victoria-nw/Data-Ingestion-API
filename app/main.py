from fastapi import FastAPI

app = FastAPI(title="Data Ingestion")

@app.get("/health")
def health():
    return {"status": "ok"}
