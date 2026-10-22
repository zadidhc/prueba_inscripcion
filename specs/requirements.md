# Especificación de Requisitos del Sistema (SRS)
## Sistema de Gestión de Inscripciones y Asistencia a Eventos Universitarios

### 1. Visión General y Objetivos
El sistema centraliza y automatiza la administración de eventos académicos (conferencias, talleres y seminarios), el registro de participantes (estudiantes, docentes, externos), el control de cupos, el registro de asistencia por sesiones y la emisión de certificados en PDF para aquellos participantes que cumplan con la asistencia obligatoria.

### 2. Actores y Roles
- **Administrador (`admin`)**: Gestiona eventos académicos, sesiones, cupos, estados de inscripciones, consulta métricas en el panel y genera certificados.
- **Personal de Registro (`staff`)**: Consulta inscripciones, busca participantes por documento de identificación y registra asistencias a las sesiones.
- **Participante (`participant` / público)**: Consulta eventos abiertos, se inscribe proporcionando sus datos y consulta el estado de su inscripción y certificado.

### 3. Requisitos Funcionales (RF)
- **RF-01: Gestión de Eventos Académicos**
  - CRUD de eventos: ID único, nombre, descripción, fecha/hora, lugar, capacidad máxima (> 0) y estado de inscripción (`ABIERTA`, `CERRADA`).
  - Definición y gestión de sesiones programadas por evento (al menos una sesión obligatoria por defecto o sesiones explícitas para control de asistencia).
- **RF-02: Inscripción de Participantes**
  - Registro con: Documento de identidad (DNI), Nombres y apellidos, Correo electrónico, Tipo de participante (`estudiante`, `docente`, `externo`) y Evento seleccionado.
  - Generación de código único de inscripción (ej. `INS-XXXXXX`).
  - Validación de eventos abiertos y disponibilidad de cupo.
- **RF-03: Gestión de Inscripciones**
  - Consulta y búsqueda por documento de identidad, filtro por evento y por estado (`INSCRITO`, `CANCELADO`, `FINALIZADO`).
  - Posibilidad de anulación/cancelación de inscripciones por parte del administrador.
- **RF-04: Control de Asistencia por Sesiones**
  - Registro de asistencia por documento de identidad a una sesión específica del evento.
  - Validación de inscripción activa (no cancelada ni inexistente).
  - Listado de asistentes y no asistentes por sesión y por evento.
- **RF-05: Verificación y Emisión de Certificados**
  - Cálculo de elegibilidad: participante que registre asistencia a todas las sesiones obligatorias del evento.
  - Descarga/Generación de certificado en PDF oficial con metadatos universitarios, código de validación, nombre del participante, evento, horas académicas/fecha.
- **RF-06: Panel de Control y Reportes**
  - Métricas agregadas: Total de eventos, eventos con inscripciones abiertas, total de participantes inscritos, asistencias totales y participantes elegibles para certificado.
  - Desglose por evento.

### 4. Reglas de Negocio (RN)
- **RN-01**: Cada evento posee un identificador único numérico o alfanumérico.
- **RN-02**: La capacidad máxima de un evento debe ser estrictamente mayor a 0.
- **RN-03**: No se permite registrar nuevos participantes cuando las inscripciones del evento estén cerradas (`CERRADA`).
- **RN-04**: No se puede exceder la capacidad máxima de participantes inscritos activos.
- **RN-05**: Un participante no puede inscribirse más de una vez en el mismo evento (DNI + evento_id único para inscripciones activas).
- **RN-06**: Un participante puede inscribirse libremente en diferentes eventos.
- **RN-07**: Solo participantes con inscripción en estado `INSCRITO` pueden registrar asistencia.
- **RN-08**: No se permite registrar dos veces la asistencia de un participante en la misma sesión (duplicidad rechazada).
- **RN-09**: Una inscripción en estado `CANCELADO` o no existente no puede registrar asistencia.
- **RN-10**: Solo los participantes elegibles (100% de asistencias a sesiones obligatorias del evento) pueden generar u obtener certificado.
- **RN-11**: Todos los campos obligatorios se validan rigurosamente antes de persistir la operación.
- **RN-12**: Los errores se notifican con códigos HTTP y mensajes estructurados y claros en español.

### 5. Requisitos No Funcionales (RNF)
- **RNF-01**: Usabilidad - Interfaz moderna, clara y accesible en español, con diseño adaptable (desktop y móvil).
- **RNF-02**: Integridad - Transacciones atómicas en base de datos SQLite y control de concurrencia de cupos.
- **RNF-03**: Seguridad - Autenticación y control de acceso por roles (Admin, Personal de Registro, Público) con tokens o cabeceras seguras; almacenamiento seguro de contraseñas.
- **RNF-04**: Mantenibilidad - Arquitectura MVC desacoplada (Modelos, Vistas separadas, Controladores/Routers, Servicios, Repositorios, Esquemas Pydantic).
- **RNF-05**: Persistencia - Almacenamiento relacional permanente en SQLite (`universidad_eventos.db`).
- **RNF-06**: Compatibilidad - Estándares web HTML5, CSS3 y JavaScript ES6+ sin frameworks pesados, compatible con navegadores modernos.
