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
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    processed_files = 0
    for name in os.listdir(folder):
        if not name.endswith(".csv"):
            continue
        
        try:
            path = os.path.join(folder, name)
            df = pd.read_csv(path)
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
