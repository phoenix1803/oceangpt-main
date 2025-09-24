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
        # Count existing data
        profile_count = db.query(models.Profile).count()
        measurement_count = db.query(models.Measurement).count()
        
        # Delete all profiles (cascade will handle measurements)
        db.query(models.Profile).delete(synchronize_session=False)
        
        # Commit the transaction
        db.commit()
        
        return {
            "status": "success", 
            "message": f"Successfully deleted {profile_count} profiles and {measurement_count} measurements"
        }
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        print(f"Reset database error: {error_msg}")  # For debugging
        raise HTTPException(status_code=500, detail=f"Error resetting database: {error_msg}")


@router.post("/reset-tables")
def reset_tables(db: Session = Depends(get_db)):
    """Alternative reset method - recreate database tables"""
    try:
        from ..db import Base, engine
        
        # Count existing data
        profile_count = db.query(models.Profile).count()
        measurement_count = db.query(models.Measurement).count()
        
        # Close the current session
        db.close()
        
        # Drop and recreate tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        return {
            "status": "success", 
            "message": f"Successfully reset database (removed {profile_count} profiles and {measurement_count} measurements)"
        }
    except Exception as e:
        error_msg = str(e)
        print(f"Reset tables error: {error_msg}")  # For debugging
        raise HTTPException(status_code=500, detail=f"Error resetting tables: {error_msg}")
