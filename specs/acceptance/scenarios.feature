# language: es
Característica: Gestión Integral de Eventos, Inscripciones, Asistencias y Certificados

  Escenario: Registro exitoso de un evento académico
    Dado que un administrador autenticado accede al módulo de eventos
    Cuando envía los datos del evento con nombre "Congreso de IA", capacidad 50 e inscripciones "ABIERTA"
    Entonces el evento queda registrado con un ID único y visible en el catálogo de eventos

  Escenario: Validación de capacidad mayor a cero
    Dado que un administrador intenta registrar un evento
    Cuando ingresa una capacidad máxima igual o menor a 0
    Entonces el sistema rechaza la solicitud con un error de validación claro

  Escenario: Inscripción exitosa de un participante
    Dado un evento existente con inscripciones abiertas y cupos disponibles
    Cuando un estudiante con DNI "71234567" se inscribe proporcionando sus datos completos
    Entonces el sistema genera un código de inscripción y el estado inicial es "INSCRITO"

  Escenario: Rechazo de inscripción duplicada en el mismo evento
    Dado que un participante con DNI "71234567" ya está inscrito en el evento "Congreso de IA"
    Cuando intenta inscribirse nuevamente en el mismo evento
    Entonces el sistema rechaza la inscripción indicando que ya se encuentra registrado

  Escenario: Rechazo de inscripción cuando las inscripciones están cerradas
    Dado un evento con estado de inscripción "CERRADA"
    Cuando un participante intenta inscribirse
    Entonces el sistema rechaza la solicitud indicando que las inscripciones están cerradas

  Escenario: Rechazo de inscripción al alcanzar la capacidad máxima
    Dado un evento cuya capacidad máxima de participantes ya fue cubierta
    Cuando un nuevo participante intenta inscribirse
    Entonces el sistema deniega el registro por falta de cupos disponibles

  Escenario: Registro exitoso de asistencia
    Dado un participante con inscripción activa "INSCRITO" en el evento
    Cuando el personal de registro marca asistencia con el DNI del participante a una sesión programada
    Entonces la asistencia queda registrada con fecha y hora

  Escenario: Rechazo de duplicidad en asistencia a la misma sesión
    Dado que un participante ya registró asistencia a la "Sesión 1"
    Cuando el personal intenta registrar nuevamente la asistencia del mismo participante a dicha sesión
    Entonces el sistema rechaza la operación informando que la asistencia ya fue registrada previamente

  Escenario: Impedir asistencia a inscripciones canceladas
    Dado un participante cuya inscripción se encuentra en estado "CANCELADO"
    Cuando se intenta registrar su asistencia a una sesión
    Entonces el sistema rechaza el registro indicando que la inscripción no está activa

  Escenario: Elegibilidad y generación de certificado PDF
    Dado un participante que asistió a todas las sesiones obligatorias del evento
    Cuando se consulta su elegibilidad
    Entonces el sistema confirma que es elegible y permite descargar su certificado oficial en formato PDF
