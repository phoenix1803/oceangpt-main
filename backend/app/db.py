from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import tempfile
from pathlib import Path

def get_database_url():
    """Get database URL, handling read-only file systems like Streamlit Cloud"""
    
    # If DATABASE_URL is explicitly set, use it
    if "DATABASE_URL" in os.environ:
        return os.environ["DATABASE_URL"]
    
    # Check if we're likely on Streamlit Cloud (read-only filesystem)
    if os.getenv("STREAMLIT_SHARING_MODE") or os.getenv("STREAMLIT_CLOUD"):
        # Use in-memory SQLite for Streamlit Cloud
        return "sqlite:///:memory:"
    
    # Try to create a database in a writable location
    possible_locations = [
        # Try temp directory first
        Path(tempfile.gettempdir()) / "argo.db",
        # Try user's home directory
        Path.home() / ".argo" / "argo.db",
        # Try current working directory
        Path.cwd() / "argo.db",
        # Try backend data directory (local development)
        Path(__file__).parent.parent / "data" / "argo.db"
    ]
    
    for db_path in possible_locations:
        try:
            # Create parent directory if needed
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Test if we can write to this location
            test_file = db_path.parent / "test_write.tmp"
            test_file.touch()
            test_file.unlink()
            
            return f"sqlite:///{db_path}"
        except (PermissionError, OSError):
            continue
    
    # Fallback to in-memory database
    print("Warning: Could not find writable location for database, using in-memory SQLite")
    return "sqlite:///:memory:"

DATABASE_URL = get_database_url()
print(f"Using database: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False  # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
