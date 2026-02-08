from fastapi import FastAPI

from app.db import Base, engine, SessionLocal
from app.routers import auth
from app.seed import seed_data

app = FastAPI(title="PH Admin Core")

app.include_router(auth.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
