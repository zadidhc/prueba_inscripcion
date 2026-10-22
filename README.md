# Sistema de Gestión de Inscripciones y Asistencia a Eventos Universitarios
Desarrollado bajo la metodología **Spec-Driven Development (SDD / Spec-First)** con **Python 3, FastAPI, SQLite y Frontend desacoplado (HTML5/CSS3/JavaScript ES6)**.

---

## 1. Descripción y Objetivos
Aplicación web universitaria integral que automatiza y centraliza:
- Registro, actualización y control de estado de eventos académicos (conferencias, talleres y seminarios).
- Gestión de cupos y sesiones obligatorias por evento.
- Registro de inscripción pública de participantes (estudiantes, docentes y externos) con generación de código único (`INS-XXXXXX`).
- Control y marcado de asistencia a sesiones mediante documento de identidad (DNI).
- Validación de elegibilidad y emisión de certificados oficiales en formato PDF con firma y código de verificación.
- Panel administrativo con métricas e indicadores en tiempo real.

---

## 2. Arquitectura del Sistema
El proyecto sigue el patrón **Monolito Modular con MVC** adaptado a FastAPI y Frontend desacoplado:
- **Model**: Entidades relacionales SQLAlchemy (`Event`, `EventSession`, `Participant`, `Registration`, `Attendance`, `User`).
- **View**: Frontend desacoplado en `/frontend` (HTML semántico, diseño CSS responsivo universitario y JavaScript nativo).
- **Controller**: Routers FastAPI en `/backend/app/controllers/`.
- **Services**: Lógica de negocio y reglas del dominio en `/backend/app/services/` (validaciones de cupo, control de asistencia, elegibilidad, PDF).
- **Repositories**: Aislamiento de acceso a datos en `/backend/app/repositories/`.
- **Schemas**: Contratos Pydantic v2 en `/backend/app/schemas/`.

---

## 3. Estructura del Proyecto
```text
2026-10-22/
│
├── README.md                          # Documentación e instrucciones
├── pytest.ini                         # Configuración del motor de pruebas
│
├── specs/                             # Especificaciones Spec-Driven
│   ├── requirements.md                # Requisitos funcionales y no funcionales
│   ├── architecture.md                # Arquitectura técnica y decisiones
│   ├── features/                      # Especificación de funcionalidades
│   │   └── features.md
│   ├── contracts/                     # Contrato OpenAPI 3.0 en YAML
│   │   └── openapi.yaml
│   └── acceptance/                    # Escenarios de aceptación Given-When-Then
│       └── scenarios.feature
│
├── backend/                           # Backend FastAPI
│   ├── requirements.txt               # Dependencias Python
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Inicialización de FastAPI y montaje estático
│   │   ├── core/                      # Configuración, base de datos y seguridad JWT
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/                    # Modelos de dominio SQLAlchemy
│   │   │   └── models.py
│   │   ├── schemas/                   # Esquemas de validación Pydantic
│   │   │   └── schemas.py
│   │   ├── repositories/              # Repositorios de acceso a datos
│   │   │   └── repositories.py
│   │   ├── services/                  # Servicios de lógica de negocio y generador PDF
│   │   │   ├── services.py
│   │   │   └── pdf_service.py
│   │   └── controllers/               # Controladores y endpoints HTTP
│   │       └── controllers.py
│   │
│   └── tests/                         # Pruebas automatizadas
│       ├── conftest.py                # Fixtures y SQLite en memoria aislado
│       ├── acceptance/                # Pruebas de aceptación y reglas de negocio
│       │   └── test_features.py
│       └── contract/                  # Validación de contrato OpenAPI
│           └── test_openapi.py
│
└── frontend/                          # Aplicación Web Frontend
    ├── index.html                     # Vista principal SPA
    ├── css/
    │   └── styles.css                 # Identidad visual universitaria
    └── js/
        ├── api.js                     # Cliente HTTP con FastAPI
        └── app.js                     # Control de interfaz, eventos y roles
```

---

## 4. Usuarios y Credenciales por Defecto (Semilla)
Al iniciar la aplicación, se crean automáticamente las credenciales institucionales:

| Rol | Usuario | Contraseña | Permisos |
|---|---|---|---|
| **Administrador** | `admin` | `admin123` | Control total: Crear/editar eventos, cerrar inscripciones, cancelar inscripciones, ver panel de métricas y generar reportes. |
| **Personal de Registro** | `staff` | `staff123` | Marcar asistencia por DNI, consultar participantes inscritos y verificar elegibilidad. |
| **Público / Participante** | Sin login | - | Ver eventos abiertos, inscribirse, consultar su inscripción y descargar su certificado si es elegible. |

---

## 5. Instrucciones de Instalación y Ejecución

### 5.1. Requisitos Previos
- Python 3.10 o superior (verificado con Python 3.13 en Windows).

### 5.2. Configuración del Entorno Virtual e Instalación de Dependencias
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt
```

### 5.3. Iniciar el Servidor de Aplicación (Backend + Frontend)
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Aplicación Web (Frontend)**: [http://localhost:8000/](http://localhost:8000/)
- **Documentación Interactiva Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Especificación OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 6. Ejecución de Pruebas Automatizadas
Para ejecutar la suite completa de pruebas de aceptación, reglas de negocio y contrato OpenAPI:
```bash
pytest -v
```
Las pruebas utilizan SQLite en memoria (`sqlite:///:memory:`) con aislamiento por cada función de prueba.
