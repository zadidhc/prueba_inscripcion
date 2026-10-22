import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import engine, SessionLocal
from backend.app.models.models import Base, User
from backend.app.core.security import get_password_hash
from backend.app.controllers.controllers import router as api_router

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Semilla de usuarios iniciales si no existen
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                full_name="Administrador del Sistema",
                role="admin"
            )
            db.add(admin)

        staff = db.query(User).filter(User.username == "staff").first()
        if not staff:
            staff = User(
                username="staff",
                password_hash=get_password_hash("staff123"),
                full_name="Personal de Registro Académico",
                role="staff"
            )
            db.add(staff)

        db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Sistema de Gestión de Inscripciones y Asistencia a Eventos Universitarios",
    lifespan=lifespan
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas de la API
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Montar frontend estático si existe la carpeta
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
