from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
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
    from .db import DATABASE_URL, SessionLocal
    
    # Test database connection
    db_status = "ok"
    db_info = DATABASE_URL
    
    try:
        db = SessionLocal()
        # Try a simple query
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "database": {
            "status": db_status,
            "url": db_info.replace(str(Path.home()), "~") if "sqlite" in db_info else db_info  # Hide full paths
        }
    }

app.include_router(ingest.router)
app.include_router(profiles.router)
app.include_router(chat.router)
