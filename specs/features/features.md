# Especificación de Características: Gestión de Eventos, Inscripciones, Asistencia y Certificados

## Característica 1: Eventos Académicos y Sesiones (RF-01)
- **Creación**: Permite a un administrador registrar un evento con nombre, descripción, fecha/hora, lugar, capacidad > 0 y estado de inscripción (`ABIERTA` o `CERRADA`).
- **Sesiones**: Cada evento cuenta con al menos una sesión para registro de asistencia. El administrador puede añadir sesiones indicando si son de asistencia obligatoria.
- **Edición y Cierre**: El administrador puede cambiar estado de inscripciones a `CERRADA` o actualizar capacidad y datos generales.

## Característica 2: Inscripción de Participantes (RF-02 y RF-03)
- **Registro**: Participante ingresa DNI, Nombres y Apellidos, Correo, Tipo (`estudiante`, `docente`, `externo`) y selecciona un evento abierto.
- **Validaciones**:
  - Evento debe existir y tener inscripciones `ABIERTA`.
  - Capacidad máxima no debe haber sido alcanzada.
  - El DNI no debe tener una inscripción previa en estado `INSCRITO` para el mismo evento.
- **Estados**:
  - `INSCRITO`: Estado inicial válido.
  - `CANCELADO`: Modificado por administrador.
  - `FINALIZADO`: Cuando el evento ya concluyó.
- **Búsqueda y Filtros**: Búsqueda por DNI, filtro por evento y por estado.

## Característica 3: Control de Asistencia (RF-04)
- **Marcado de Asistencia**: Personal de registro selecciona la sesión e ingresa el DNI del participante.
- **Validaciones**:
  - El participante debe tener inscripción en estado `INSCRITO` en el evento al que pertenece la sesión.
  - Si la inscripción está `CANCELADO` o no existe, se rechaza.
  - Si ya tiene asistencia registrada en la misma sesión, se rechaza la duplicidad.
- **Visualización**: Listado de participantes con estado de asistencia (Presente / Ausente).

## Característica 4: Elegibilidad y Emisión de Certificados (RF-05)
- **Cálculo de Elegibilidad**: Un participante es elegible si asistió al 100% de las sesiones obligatorias del evento.
- **Descarga de Certificado PDF**: Endpoint `GET /api/v1/certificates/{registration_id}/pdf` genera un documento PDF válido y elegante.

## Característica 5: Dashboard y Métricas (RF-06)
- **Indicadores en Tiempo Real**:
  - Total de eventos.
  - Eventos abiertos.
  - Total de inscritos.
  - Total de asistencias registradas.
  - Total de participantes con certificación lograda.
  - Resumen por evento individual.
