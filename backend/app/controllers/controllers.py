from typing import List, Optional
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_role, create_access_token, verify_password
from backend.app.models.models import User
from backend.app.schemas.schemas import (
    LoginRequest, LoginResponse, UserResponse,
    EventCreate, EventUpdate, EventResponse, EventDetailResponse,
    SessionCreate, SessionResponse,
    RegistrationCreate, RegistrationResponse, RegistrationStatusUpdate,
    AttendanceCreate, AttendanceResponse, ParticipantAttendanceReport,
    CertificateEligibilityResponse, DashboardMetrics
)
from backend.app.repositories.repositories import UserRepository, EventRepository, RegistrationRepository
from backend.app.services.services import (
    EventService, RegistrationService, AttendanceService, CertificateService, DashboardService
)
from fastapi import HTTPException

router = APIRouter()

# ----------------- AUTENTICACIÓN -----------------
@router.post("/auth/login", response_model=LoginResponse, summary="Iniciar sesión")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos."
        )
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/auth/me", response_model=UserResponse, summary="Usuario actual")
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

# ----------------- EVENTOS -----------------
@router.get("/events", response_model=List[EventResponse], summary="Listar eventos académicos")
def list_events(status: Optional[str] = None, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    events = repo.list_all(status=status)
    results = []
    for e in events:
        active_count = repo.count_active_registrations(e.id)
        results.append(
            EventResponse(
                id=e.id,
                title=e.title,
                description=e.description,
                start_time=e.start_time,
                location=e.location,
                max_capacity=e.max_capacity,
                status=e.status,
                active_registrations_count=active_count
            )
        )
    return results

@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED, summary="Crear evento académico")
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    service = EventService(db)
    created = service.create_event(data)
    return EventResponse(
        id=created.id,
        title=created.title,
        description=created.description,
        start_time=created.start_time,
        location=created.location,
        max_capacity=created.max_capacity,
        status=created.status,
        active_registrations_count=0
    )

@router.get("/events/{event_id}", response_model=EventDetailResponse, summary="Detalle de evento y sesiones")
def get_event(event_id: int, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    event = repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado.")
    active_count = repo.count_active_registrations(event.id)
    sessions = repo.get_event_sessions(event.id)
    return EventDetailResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        location=event.location,
        max_capacity=event.max_capacity,
        status=event.status,
        active_registrations_count=active_count,
        sessions=[SessionResponse.model_validate(s) for s in sessions]
    )

@router.put("/events/{event_id}", response_model=EventResponse, summary="Actualizar evento")
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    service = EventService(db)
    updated = service.update_event(event_id, data)
    active_count = service.repo.count_active_registrations(updated.id)
    return EventResponse(
        id=updated.id,
        title=updated.title,
        description=updated.description,
        start_time=updated.start_time,
        location=updated.location,
        max_capacity=updated.max_capacity,
        status=updated.status,
        active_registrations_count=active_count
    )

@router.post("/events/{event_id}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED, summary="Agregar sesión al evento")
def add_session(
    event_id: int,
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    service = EventService(db)
    session = service.add_session(event_id, data)
    return SessionResponse.model_validate(session)

# ----------------- INSCRIPCIONES -----------------
@router.post("/registrations", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED, summary="Inscribir participante")
def register_participant(data: RegistrationCreate, db: Session = Depends(get_db)):
    service = RegistrationService(db)
    reg = service.register_participant(data)
    return RegistrationResponse(
        id=reg.id,
        code=reg.code,
        event_id=reg.event_id,
        event_title=reg.event.title,
        participant_id=reg.participant_id,
        document_id=reg.participant.document_id,
        full_name=reg.participant.full_name,
        email=reg.participant.email,
        participant_type=reg.participant.participant_type,
        status=reg.status,
        created_at=reg.created_at
    )

@router.get("/registrations", response_model=List[RegistrationResponse], summary="Consultar y filtrar inscripciones")
def list_registrations(
    event_id: Optional[int] = None,
    document_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    repo = RegistrationRepository(db)
    regs = repo.list_registrations(event_id=event_id, document_id=document_id, status=status)
    return [
        RegistrationResponse(
            id=r.id,
            code=r.code,
            event_id=r.event_id,
            event_title=r.event.title,
            participant_id=r.participant_id,
            document_id=r.participant.document_id,
            full_name=r.participant.full_name,
            email=r.participant.email,
            participant_type=r.participant.participant_type,
            status=r.status,
            created_at=r.created_at
        ) for r in regs
    ]

@router.patch("/registrations/{registration_id}/status", response_model=RegistrationResponse, summary="Cambiar estado de inscripción")
def update_registration_status(
    registration_id: int,
    data: RegistrationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    service = RegistrationService(db)
    reg = service.update_status(registration_id, data.status)
    return RegistrationResponse(
        id=reg.id,
        code=reg.code,
        event_id=reg.event_id,
        event_title=reg.event.title,
        participant_id=reg.participant_id,
        document_id=reg.participant.document_id,
        full_name=reg.participant.full_name,
        email=reg.participant.email,
        participant_type=reg.participant.participant_type,
        status=reg.status,
        created_at=reg.created_at
    )

# ----------------- ASISTENCIA -----------------
@router.post("/attendances", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED, summary="Registrar asistencia")
def record_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "staff"]))
):
    service = AttendanceService(db)
    att = service.register_attendance(data, registered_by_user_id=current_user.id)
    return AttendanceResponse(
        id=att.id,
        session_id=att.session_id,
        registration_id=att.registration_id,
        participant_name=att.registration.participant.full_name,
        document_id=att.registration.participant.document_id,
        registered_at=att.registered_at
    )

@router.get("/events/{event_id}/attendances", response_model=List[ParticipantAttendanceReport], summary="Matriz de asistencia del evento")
def get_event_attendance(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "staff"]))
):
    service = AttendanceService(db)
    return service.get_event_attendance_matrix(event_id)

# ----------------- CERTIFICADOS -----------------
@router.get("/events/{event_id}/certificates/eligible", response_model=List[CertificateEligibilityResponse], summary="Consultar participantes elegibles para certificado")
def list_eligible_participants(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "staff"]))
):
    att_service = AttendanceService(db)
    matrix = att_service.get_event_attendance_matrix(event_id)
    results = []
    for p in matrix:
        reason = "Cumple con el 100% de asistencia obligatoria." if p.is_eligible_certificate else f"Asistió a {p.attended_sessions} de {p.total_mandatory_sessions} sesiones requeridas."
        results.append(
            CertificateEligibilityResponse(
                registration_id=p.registration_id,
                code=p.code,
                document_id=p.document_id,
                full_name=p.full_name,
                is_eligible=p.is_eligible_certificate,
                reason=reason
            )
        )
    return results

@router.get("/certificates/{registration_id}/pdf", summary="Descargar certificado en PDF")
def download_certificate_pdf(registration_id: int, db: Session = Depends(get_db)):
    cert_service = CertificateService(db)
    pdf_bytes = cert_service.generate_pdf(registration_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Certificado_Inscripcion_{registration_id}.pdf"
        }
    )

# ----------------- DASHBOARD / REPORTES -----------------
@router.get("/dashboard/metrics", response_model=DashboardMetrics, summary="Métricas del panel administrativo")
def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    service = DashboardService(db)
    return service.get_metrics()
