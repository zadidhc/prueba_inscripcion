from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.models import Event, EventSession, Registration, Participant, Attendance, User

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, event_id: int) -> Optional[Event]:
        return self.db.query(Event).filter(Event.id == event_id).first()

    def list_all(self, status: Optional[str] = None) -> List[Event]:
        query = self.db.query(Event)
        if status:
            query = query.filter(Event.status == status)
        return query.order_by(Event.id.desc()).all()

    def create(self, event: Event) -> Event:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update(self, event: Event) -> Event:
        self.db.commit()
        self.db.refresh(event)
        return event

    def count_active_registrations(self, event_id: int) -> int:
        return self.db.query(Registration).filter(
            Registration.event_id == event_id,
            Registration.status == "INSCRITO"
        ).count()

    def add_session(self, session: EventSession) -> EventSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_by_id(self, session_id: int) -> Optional[EventSession]:
        return self.db.query(EventSession).filter(EventSession.id == session_id).first()

    def get_event_sessions(self, event_id: int) -> List[EventSession]:
        return self.db.query(EventSession).filter(EventSession.event_id == event_id).order_by(EventSession.session_date.asc()).all()


class RegistrationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, registration_id: int) -> Optional[Registration]:
        return self.db.query(Registration).filter(Registration.id == registration_id).first()

    def get_by_code(self, code: str) -> Optional[Registration]:
        return self.db.query(Registration).filter(Registration.code == code).first()

    def get_participant_by_document(self, document_id: str) -> Optional[Participant]:
        return self.db.query(Participant).filter(Participant.document_id == document_id).first()

    def create_participant(self, participant: Participant) -> Participant:
        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def get_active_registration(self, event_id: int, participant_id: int) -> Optional[Registration]:
        return self.db.query(Registration).filter(
            Registration.event_id == event_id,
            Registration.participant_id == participant_id,
            Registration.status == "INSCRITO"
        ).first()

    def create_registration(self, registration: Registration) -> Registration:
        self.db.add(registration)
        self.db.commit()
        self.db.refresh(registration)
        return registration

    def list_registrations(
        self,
        event_id: Optional[int] = None,
        document_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Registration]:
        query = self.db.query(Registration).join(Participant)
        if event_id:
            query = query.filter(Registration.event_id == event_id)
        if document_id:
            query = query.filter(Participant.document_id == document_id)
        if status:
            query = query.filter(Registration.status == status)
        return query.order_by(Registration.id.desc()).all()

    def update(self, registration: Registration) -> Registration:
        self.db.commit()
        self.db.refresh(registration)
        return registration


class AttendanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_attendance(self, session_id: int, registration_id: int) -> Optional[Attendance]:
        return self.db.query(Attendance).filter(
            Attendance.session_id == session_id,
            Attendance.registration_id == registration_id
        ).first()

    def create(self, attendance: Attendance) -> Attendance:
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def get_attendances_by_registration(self, registration_id: int) -> List[Attendance]:
        return self.db.query(Attendance).filter(Attendance.registration_id == registration_id).all()

    def count_total(self) -> int:
        return self.db.query(Attendance).count()


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
