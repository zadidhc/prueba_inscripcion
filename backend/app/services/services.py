import uuid
from datetime import datetime
from typing import List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.models import Event, EventSession, Registration, Participant, Attendance, User
from backend.app.schemas.schemas import (
    EventCreate, EventUpdate, SessionCreate, RegistrationCreate, AttendanceCreate,
    DashboardMetrics, EventMetricItem, ParticipantAttendanceReport, CertificateEligibilityResponse
)
from backend.app.repositories.repositories import (
    EventRepository, RegistrationRepository, AttendanceRepository, UserRepository
)
from backend.app.services.pdf_service import generate_certificate_pdf

class EventService:
    def __init__(self, db: Session):
        self.repo = EventRepository(db)

    def create_event(self, data: EventCreate) -> Event:
        # RN-02: Capacidad máxima > 0
        if data.max_capacity <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La capacidad máxima de un evento debe ser estrictamente mayor que cero."
            )
        event = Event(
            title=data.title,
            description=data.description,
            start_time=data.start_time,
            location=data.location,
            max_capacity=data.max_capacity,
            status=data.status
        )
        saved_event = self.repo.create(event)
        # Crear por defecto la sesión principal del evento si no se definen otras
        default_session = EventSession(
            event_id=saved_event.id,
            title="Sesión General Obligatoria",
            session_date=saved_event.start_time,
            is_mandatory=True
        )
        self.repo.add_session(default_session)
        return saved_event

    def update_event(self, event_id: int, data: EventUpdate) -> Event:
        event = self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento académico no encontrado.")

        if data.max_capacity is not None:
            if data.max_capacity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="La capacidad máxima debe ser mayor que cero."
                )
            event.max_capacity = data.max_capacity

        if data.title is not None:
            event.title = data.title
        if data.description is not None:
            event.description = data.description
        if data.start_time is not None:
            event.start_time = data.start_time
        if data.location is not None:
            event.location = data.location
        if data.status is not None:
            event.status = data.status

        return self.repo.update(event)

    def add_session(self, event_id: int, data: SessionCreate) -> EventSession:
        event = self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento académico no encontrado.")
        session = EventSession(
            event_id=event_id,
            title=data.title,
            session_date=data.session_date,
            is_mandatory=data.is_mandatory
        )
        return self.repo.add_session(session)


class RegistrationService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)
        self.reg_repo = RegistrationRepository(db)

    def register_participant(self, data: RegistrationCreate) -> Registration:
        event = self.event_repo.get_by_id(data.event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El evento especificado no existe.")

        # RN-03: No permitir cuando inscripciones estén cerradas
        if event.status != "ABIERTA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las inscripciones para este evento se encuentran actualmente CERRADAS."
            )

        # RN-04: No superar capacidad máxima
        active_count = self.event_repo.count_active_registrations(event.id)
        if active_count >= event.max_capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Se ha alcanzado la capacidad máxima ({event.max_capacity} cupos) para este evento."
            )

        # Buscar o crear participante por documento
        participant = self.reg_repo.get_participant_by_document(data.document_id.strip())
        if not participant:
            participant = Participant(
                document_id=data.document_id.strip(),
                full_name=data.full_name.strip(),
                email=data.email.strip().lower(),
                participant_type=data.participant_type
            )
            participant = self.reg_repo.create_participant(participant)
        else:
            # Actualizar nombres y correo si variaron
            participant.full_name = data.full_name.strip()
            participant.email = data.email.strip().lower()
            participant.participant_type = data.participant_type
            self.db.commit()

        # RN-05: Un participante no puede inscribirse dos veces al mismo evento
        existing_reg = self.reg_repo.get_active_registration(event.id, participant.id)
        if existing_reg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El participante ya se encuentra registrado con una inscripción activa en este evento."
            )

        # Generar código único de inscripción
        code = f"INS-{event.id}-{uuid.uuid4().hex[:6].upper()}"
        registration = Registration(
            code=code,
            event_id=event.id,
            participant_id=participant.id,
            status="INSCRITO"
        )
        return self.reg_repo.create_registration(registration)

    def update_status(self, registration_id: int, new_status: str) -> Registration:
        reg = self.reg_repo.get_by_id(registration_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripción no encontrada.")
        reg.status = new_status
        return self.reg_repo.update(reg)


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)
        self.reg_repo = RegistrationRepository(db)
        self.att_repo = AttendanceRepository(db)

    def register_attendance(self, data: AttendanceCreate, registered_by_user_id: int = None) -> Attendance:
        session = self.event_repo.get_session_by_id(data.session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión programada no encontrada.")

        participant = self.reg_repo.get_participant_by_document(data.document_id.strip())
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No existe participante registrado con el documento de identidad proporcionado."
            )

        # Obtener inscripción del participante en el evento de la sesión
        registration = self.db.query(Registration).filter(
            Registration.event_id == session.event_id,
            Registration.participant_id == participant.id
        ).first()

        if not registration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El participante no está inscrito en el evento al que corresponde esta sesión."
            )

        # RN-07 y RN-09: Solo inscripciones activas (no canceladas)
        if registration.status == "CANCELADO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La inscripción del participante se encuentra CANCELADA. No puede registrar asistencia."
            )
        if registration.status != "INSCRITO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La inscripción tiene estado '{registration.status}'. Solo inscripciones activas pueden marcar asistencia."
            )

        # RN-08: No permitir duplicidad en la misma sesión
        existing_att = self.att_repo.get_attendance(session.id, registration.id)
        if existing_att:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La asistencia de este participante ya fue registrada previamente para esta sesión."
            )

        attendance = Attendance(
            session_id=session.id,
            registration_id=registration.id,
            registered_by_user_id=registered_by_user_id
        )
        return self.att_repo.create(attendance)

    def get_event_attendance_matrix(self, event_id: int) -> List[ParticipantAttendanceReport]:
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado.")

        sessions = self.event_repo.get_event_sessions(event_id)
        mandatory_sessions = [s for s in sessions if s.is_mandatory]
        total_mandatory = len(mandatory_sessions)

        registrations = self.db.query(Registration).filter(Registration.event_id == event_id).all()
        results = []

        for reg in registrations:
            attendances = self.att_repo.get_attendances_by_registration(reg.id)
            attended_session_ids = {a.session_id for a in attendances}

            # Contar asistencias a sesiones obligatorias
            mandatory_attended = sum(1 for s in mandatory_sessions if s.id in attended_session_ids)

            # RN-10: Elegible si asistió a todas las sesiones obligatorias
            is_eligible = (
                reg.status == "INSCRITO" and
                total_mandatory > 0 and
                mandatory_attended == total_mandatory
            )

            pct = (mandatory_attended / total_mandatory * 100) if total_mandatory > 0 else 0.0

            results.append(
                ParticipantAttendanceReport(
                    registration_id=reg.id,
                    code=reg.code,
                    document_id=reg.participant.document_id,
                    full_name=reg.participant.full_name,
                    participant_type=reg.participant.participant_type,
                    status=reg.status,
                    attended_sessions=mandatory_attended,
                    total_mandatory_sessions=total_mandatory,
                    attendance_percentage=round(pct, 1),
                    is_eligible_certificate=is_eligible
                )
            )

        return results


class CertificateService:
    def __init__(self, db: Session):
        self.db = db
        self.att_service = AttendanceService(db)
        self.reg_repo = RegistrationRepository(db)

    def check_eligibility(self, registration_id: int) -> Tuple[bool, str, Registration]:
        reg = self.reg_repo.get_by_id(registration_id)
        if not reg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscripción no encontrada.")

        if reg.status != "INSCRITO":
            return False, f"La inscripción no se encuentra activa (Estado: {reg.status}).", reg

        matrix = self.att_service.get_event_attendance_matrix(reg.event_id)
        participant_report = next((item for item in matrix if item.registration_id == reg.id), None)

        if not participant_report or not participant_report.is_eligible_certificate:
            attended = participant_report.attended_sessions if participant_report else 0
            total = participant_report.total_mandatory_sessions if participant_report else 0
            return False, f"Asistió a {attended} de {total} sesiones obligatorias requeridas (100% requerido).", reg

        return True, "Cumple con el 100% de asistencia a las sesiones obligatorias.", reg

    def generate_pdf(self, registration_id: int) -> bytes:
        is_eligible, reason, reg = self.check_eligibility(registration_id)
        if not is_eligible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Participante no elegible para certificado. {reason}"
            )

        event_date_str = reg.event.start_time.strftime("%d/%m/%Y")
        return generate_certificate_pdf(
            participant_name=reg.participant.full_name,
            document_id=reg.participant.document_id,
            event_title=reg.event.title,
            event_date=event_date_str,
            registration_code=reg.code
        )


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)
        self.att_service = AttendanceService(db)

    def get_metrics(self) -> DashboardMetrics:
        events = self.event_repo.list_all()
        total_events = len(events)
        open_events = sum(1 for e in events if e.status == "ABIERTA")

        total_regs = self.db.query(Registration).filter(Registration.status == "INSCRITO").count()
        total_atts = self.db.query(Attendance).count()

        total_eligible = 0
        events_summary = []

        for e in events:
            reg_count = self.event_repo.count_active_registrations(e.id)
            att_count = (
                self.db.query(Attendance)
                .join(EventSession)
                .filter(EventSession.event_id == e.id)
                .count()
            )
            matrix = self.att_service.get_event_attendance_matrix(e.id)
            eligible_in_event = sum(1 for p in matrix if p.is_eligible_certificate)
            total_eligible += eligible_in_event

            events_summary.append(
                EventMetricItem(
                    event_id=e.id,
                    title=e.title,
                    capacity=e.max_capacity,
                    registrations=reg_count,
                    attendances=att_count,
                    status=e.status
                )
            )

        return DashboardMetrics(
            total_events=total_events,
            open_events=open_events,
            total_registrations=total_regs,
            total_attendances=total_atts,
            total_eligible_certificates=total_eligible,
            events_summary=events_summary
        )
