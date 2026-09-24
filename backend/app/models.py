from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20))  # official / inspector / institution
    email: Mapped[str] = mapped_column(String(120), unique=True)


class Institution(Base):
    __tablename__ = "institutions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    scheme: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    registered_beneficiaries: Mapped[int] = mapped_column(Integer, default=0)
    open_time: Mapped[str] = mapped_column(String(5), default="09:00")
    close_time: Mapped[str] = mapped_column(String(5), default="17:00")


class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"))
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reported_count: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(30), default="institution")


class Camera(Base):
    __tablename__ = "cameras"
    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"))
    label: Mapped[str] = mapped_column(String(80))
    stream_url: Mapped[str] = mapped_column(String(300), default="")


class AIObservation(Base):
    __tablename__ = "ai_observations"
    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"))
    camera_id: Mapped[int | None] = mapped_column(ForeignKey("cameras.id"), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime)
    occupancy: Mapped[int] = mapped_column(Integer)
    activity: Mapped[str] = mapped_column(String(30))
    confidence: Mapped[float] = mapped_column(Float)


class Anomaly(Base):
    __tablename__ = "anomalies"
    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    kind: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(10))
    priority_score: Mapped[float] = mapped_column(Float, default=0)
    explanation: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")


class Inspection(Base):
    __tablename__ = "inspections"
    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"))
    inspector_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_surprise: Mapped[bool] = mapped_column(Boolean, default=False)
    result: Mapped[str] = mapped_column(String(30), default="pending")
    notes: Mapped[str] = mapped_column(Text, default="")


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"))
    file_path: Mapped[str] = mapped_column(String(300))
    sha256: Mapped[str] = mapped_column(String(64))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)