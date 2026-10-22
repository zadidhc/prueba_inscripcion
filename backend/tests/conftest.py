import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.models.models import Base, User
from backend.app.core.security import get_password_hash

# Usamos SQLite en memoria con StaticPool para que todas las conexiones compartan la misma instancia en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Crear usuarios semilla
    admin_user = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        full_name="Administrador Principal",
        role="admin"
    )
    staff_user = User(
        username="staff",
        password_hash=get_password_hash("staff123"),
        full_name="Personal de Registro",
        role="staff"
    )
    db.add(admin_user)
    db.add(staff_user)
    db.commit()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def admin_token(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    return res.json()["access_token"]

@pytest.fixture(scope="function")
def staff_token(client):
    res = client.post("/api/v1/auth/login", json={"username": "staff", "password": "staff123"})
    return res.json()["access_token"]
