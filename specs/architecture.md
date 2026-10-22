# Arquitectura del Sistema
## Sistema de Gestión de Inscripciones y Asistencia a Eventos Universitarios

### 1. Patrón Arquitectónico
Se adopta un **Monolito Modular con patrón MVC (Model-View-Controller)** adaptado a FastAPI y un Frontend desacoplado:

- **Model (Modelo)**: Entidades SQLAlchemy / SQLite para persistencia relacional (`Event`, `Session`, `Participant`, `Registration`, `Attendance`, `User`).
- **View (Vista)**: Frontend desacoplado en directorio `/frontend` (HTML5, Vanilla CSS moderno, JavaScript ES6) consumiendo la API REST mediante `fetch()`.
- **Controller (Controlador)**: Routers FastAPI en `/backend/app/controllers/` que reciben solicitudes HTTP, validan parámetros y delegan la lógica a los servicios.
- **Services (Servicios)**: Módulo `/backend/app/services/` donde residen las reglas de negocio, validaciones de cupos, cálculo de elegibilidad para certificados y generación de PDF.
- **Repositories (Repositorios)**: Módulo `/backend/app/repositories/` que aísla el acceso y consultas a la base de datos SQLite.
- **Schemas (Esquemas)**: Clases Pydantic v2 en `/backend/app/schemas/` para validación de contratos de entrada y salida con mensajes claros en español.

### 2. Estructura de Base de Datos (SQLite)
- `users`: id, username, password_hash, full_name, role (`admin`, `staff`).
- `events`: id, title, description, start_time, location, max_capacity, status (`ABIERTA`, `CERRADA`), created_at.
- `event_sessions`: id, event_id (FK), title, session_date, is_mandatory.
- `participants`: id, document_id (DNI único), full_name, email, participant_type (`estudiante`, `docente`, `externo`).
- `registrations`: id, code (código legible ej. `INS-2026-XXXX`), event_id (FK), participant_id (FK), status (`INSCRITO`, `CANCELADO`, `FINALIZADO`), created_at.
- `attendances`: id, session_id (FK), registration_id (FK), registered_at, registered_by_user_id (FK).

### 3. Generador de Certificados
Uso de la biblioteca estándar de Python `reportlab` para generar documentos PDF profesionales y válidos con marco institucional universitario, nombre del evento, nombre del participante, código QR/hash de verificación y firma de autoridad.

### 4. Seguridad y Roles
- Mecanismo de autenticación vía JWT (JSON Web Tokens) o sesiones HTTP seguras.
- Endpoints públicos: listado de eventos abiertos, registro de inscripción por participante, consulta pública de inscripción y descarga de certificado elegible con código.
- Endpoints protegidos para `staff` y `admin`: registro de asistencia, búsqueda de participantes y lista de inscripciones.
- Endpoints protegidos exclusivamente para `admin`: gestión de eventos (crear, editar, cerrar), anular inscripciones, panel de métricas y reportes globales.
