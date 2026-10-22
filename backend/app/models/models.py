from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(20), nullable=False) # 'admin', 'staff'
    created_at = Column(DateTime(timezone=True), default=utc_now)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(200), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    status = Column(String(20), default="ABIERTA", nullable=False) # 'ABIERTA', 'CERRADA'
    created_at = Column(DateTime(timezone=True), default=utc_now)

    sessions = relationship("EventSession", back_populates="event", cascade="all, delete-orphan")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")

class EventSession(Base):
    __tablename__ = "event_sessions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    title = Column(String(200), nullable=False)
    session_date = Column(DateTime(timezone=True), nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)

    event = relationship("Event", back_populates="sessions")
    attendances = relationship("Attendance", back_populates="session", cascade="all, delete-orphan")

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(30), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    participant_type = Column(String(30), nullable=False) # 'estudiante', 'docente', 'externo'
    created_at = Column(DateTime(timezone=True), default=utc_now)

    registrations = relationship("Registration", back_populates="participant")

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    status = Column(String(20), default="INSCRITO", nullable=False) # 'INSCRITO', 'CANCELADO', 'FINALIZADO'
    created_at = Column(DateTime(timezone=True), default=utc_now)

    event = relationship("Event", back_populates="registrations")
    participant = relationship("Participant", back_populates="registrations")
    attendances = relationship("Attendance", back_populates="registration", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("event_id", "participant_id", name="uq_event_participant"),
    )

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("event_sessions.id"), nullable=False)
    registration_id = Column(Integer, ForeignKey("registrations.id"), nullable=False)
    registered_at = Column(DateTime(timezone=True), default=utc_now)
    registered_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    session = relationship("EventSession", back_populates="attendances")
    registration = relationship("Registration", back_populates="attendances")

    __table_args__ = (
        UniqueConstraint("session_id", "registration_id", name="uq_session_registration"),
    )
