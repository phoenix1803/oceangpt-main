from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    float_id = Column(String, index=True)
    n_prof = Column(Integer, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    measurements = relationship("Measurement", back_populates="profile", cascade="all, delete-orphan")

class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), index=True)
    n_levels = Column(Integer)
    pres = Column(Float)
    temp = Column(Float)
    psal = Column(Float)

    profile = relationship("Profile", back_populates="measurements")
