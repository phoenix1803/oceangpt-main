from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal, Base, engine
from .. import models
import os
import pandas as pd

router = APIRouter(prefix="/ingest", tags=["ingest"])

# Ensure tables exist (idempotent)
Base.metadata.create_all(bind=engine, checkfirst=True)


def ingest_csv_folder(folder: str, db: Session):
    # Try to resolve the path
    import pathlib
    
    # Convert to Path object for better handling
    folder_path = pathlib.Path(folder)
    
    # If it's a relative path, try different base directories
    if not folder_path.is_absolute():
        possible_paths = [
            folder_path,  # Current working directory
            pathlib.Path.cwd() / folder_path,  # Explicit current directory
            pathlib.Path(__file__).parent.parent / folder_path,  # Relative to backend
            pathlib.Path(__file__).parent.parent.parent / folder_path,  # Relative to project root
        ]
        
        folder_path = None
        for path in possible_paths:
            if path.exists() and path.is_dir():
                folder_path = path
                break
    
    if not folder_path or not folder_path.exists():
        # List available directories for debugging
        cwd = pathlib.Path.cwd()
        backend_dir = pathlib.Path(__file__).parent.parent
        available_dirs = []
        
        for base_dir in [cwd, backend_dir]:
            if base_dir.exists():
                dirs = [d.name for d in base_dir.iterdir() if d.is_dir()]
                available_dirs.append(f"{base_dir}: {dirs}")
        
        raise FileNotFoundError(f"Folder not found: {folder}. Available directories: {'; '.join(available_dirs)}")
    
    if not folder_path.is_dir():
        raise FileNotFoundError(f"Path exists but is not a directory: {folder_path}")

    processed_files = 0
    csv_files = list(folder_path.glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in directory: {folder_path}")
    
    for csv_file in csv_files:
        name = csv_file.name
        
        try:
            df = pd.read_csv(csv_file)
            # Best-effort float_id from filename
            float_id = os.path.splitext(name)[0].split("_")[-2] if "_" in name else os.path.splitext(name)[0]

            # group by N_PROF to form profiles
            if "N_PROF" not in df.columns or "LATITUDE" not in df.columns or "LONGITUDE" not in df.columns:
                print(f"Skipping {name}: missing required columns")
                continue
                
            for n_prof, g in df.groupby("N_PROF"):
                try:
                    lat = float(g["LATITUDE"].iloc[0])
                    lon = float(g["LONGITUDE"].iloc[0])
                    profile = models.Profile(float_id=str(float_id), n_prof=int(n_prof), latitude=lat, longitude=lon)
                    db.add(profile)
                    db.flush()
                    
                    for _, row in g.iterrows():
                        m = models.Measurement(
                            profile_id=profile.id,
                            n_levels=int(row.get("N_LEVELS", 0)),
                            pres=float(row.get("PRES", 0.0)) if pd.notna(row.get("PRES")) else 0.0,
                            temp=float(row.get("TEMP", 0.0)) if pd.notna(row.get("TEMP")) else 0.0,
                            psal=float(row.get("PSAL", 0.0)) if pd.notna(row.get("PSAL")) else 0.0,
                        )
                        db.add(m)
                except Exception as e:
                    print(f"Error processing profile {n_prof} in {name}: {e}")
                    continue
                    
            processed_files += 1
        except Exception as e:
            print(f"Error processing file {name}: {e}")
            continue
            
    db.commit()
    return processed_files


@router.get("/debug")
def debug_paths():
    """Debug endpoint to show available paths and files"""
    import pathlib
    
    cwd = pathlib.Path.cwd()
    backend_dir = pathlib.Path(__file__).parent.parent
    
    info = {
        "current_working_directory": str(cwd),
        "backend_directory": str(backend_dir),
        "cwd_contents": [],
        "backend_contents": [],
        "data_directories": []
    }
    
    # List contents of current working directory
    if cwd.exists():
        info["cwd_contents"] = [str(p) for p in cwd.iterdir() if p.is_dir() or p.suffix == '.csv']
    
    # List contents of backend directory
    if backend_dir.exists():
        info["backend_contents"] = [str(p) for p in backend_dir.iterdir() if p.is_dir() or p.suffix == '.csv']
    
    # Look for data directories
    for base_dir in [cwd, backend_dir]:
        data_dir = base_dir / "data"
        if data_dir.exists():
            csv_files = list(data_dir.glob("*.csv"))
            info["data_directories"].append({
                "path": str(data_dir),
                "csv_files": [f.name for f in csv_files]
            })
    
    return info


@router.post("/csv")
def ingest_csv(folder: str):
    db = SessionLocal()
    try:
        processed_files = ingest_csv_folder(folder, db)
        return {"status": "ok", "processed_files": processed_files, "message": f"Successfully processed {processed_files} CSV files"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
