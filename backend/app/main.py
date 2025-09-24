from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import profiles, ingest, chat

app = FastAPI(title="FloatChat API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ensure tables (idempotent)
Base.metadata.create_all(bind=engine, checkfirst=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(ingest.router)
app.include_router(profiles.router)
app.include_router(chat.router)
