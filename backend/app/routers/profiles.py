from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/profiles", tags=["profiles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=schemas.ProfilesResponse)
def list_profiles(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(models.Profile)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.get("/trajectories")
def trajectories(db: Session = Depends(get_db)):
    rows = db.query(models.Profile).all()
    features = [
        {
            "type": "Feature",
            "properties": {"float_id": r.float_id, "n_prof": r.n_prof},
            "geometry": {"type": "Point", "coordinates": [r.longitude, r.latitude]},
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.delete("/reset")
def reset_database(db: Session = Depends(get_db)):
    """Reset the database by deleting all profiles and measurements"""
    try:
        # Delete all profiles (measurements will be deleted due to cascade)
        deleted_count = db.query(models.Profile).count()
        db.query(models.Profile).delete()
        db.commit()
        return {"status": "success", "message": f"Deleted {deleted_count} profiles and associated measurements"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")
