from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# Auth Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Event Schemas
class SessionBase(BaseModel):
    title: str
    session_date: datetime
    is_mandatory: bool = True

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int

class EventCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    start_time: datetime
    location: str = Field(..., min_length=2, max_length=200)
    max_capacity: int = Field(..., gt=0, description="La capacidad máxima debe ser mayor que cero")
    status: str = Field(default="ABIERTA", pattern="^(ABIERTA|CERRADA)$")

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=5)
    start_time: Optional[datetime] = None
    location: Optional[str] = Field(None, min_length=2, max_length=200)
    max_capacity: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(ABIERTA|CERRADA)$")

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    start_time: datetime
    location: str
    max_capacity: int
    status: str
    active_registrations_count: int = 0

class EventDetailResponse(EventResponse):
    sessions: List[SessionResponse] = []

# Participant & Registration Schemas
class RegistrationCreate(BaseModel):
    event_id: int
    document_id: str = Field(..., min_length=5, max_length=30)
    full_name: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    participant_type: str = Field(..., pattern="^(estudiante|docente|externo)$")

class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    event_id: int
    event_title: str
    participant_id: int
    document_id: str
    full_name: str
    email: str
    participant_type: str
    status: str
    created_at: datetime

class RegistrationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(INSCRITO|CANCELADO|FINALIZADO)$")

# Attendance Schemas
class AttendanceCreate(BaseModel):
    session_id: int
    document_id: str

class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    registration_id: int
    participant_name: str
    document_id: str
    registered_at: datetime

class ParticipantAttendanceReport(BaseModel):
    registration_id: int
    code: str
    document_id: str
    full_name: str
    participant_type: str
    status: str
    attended_sessions: int
    total_mandatory_sessions: int
    attendance_percentage: float
    is_eligible_certificate: bool

class CertificateEligibilityResponse(BaseModel):
    registration_id: int
    code: str
    document_id: str
    full_name: str
    is_eligible: bool
    reason: str

# Dashboard Metrics
class EventMetricItem(BaseModel):
    event_id: int
    title: str
    capacity: int
    registrations: int
    attendances: int
    status: str

class DashboardMetrics(BaseModel):
    total_events: int
    open_events: int
    total_registrations: int
    total_attendances: int
    total_eligible_certificates: int
    events_summary: List[EventMetricItem] = []
