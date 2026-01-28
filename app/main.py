from fastapi import FastAPI
from app.db import get_connection
from app.schemas.event import event

app = FastAPI(title="Data Ingestion Service")

@app.get("/health")
def health():
    return {"status": "ok"}



@app.get("/db/health")
def db_health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return {"database": "ok"}
    except Exception as e:
        return {
            "database": "error",
            "detail": str(e)
        }



@app.post("/events")
def ingest_event(event: event):
    return {
        "message": "event received",
        "event": event
        }
