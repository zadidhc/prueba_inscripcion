import pytest
from datetime import datetime, timedelta, timezone

def test_criterio_01_y_02_registrar_y_actualizar_evento(client, admin_token):
    # 1. Registrar un evento
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "title": "Simposio Internacional de Inteligencia Artificial",
        "description": "Encuentro de ponencias y talleres de IA y Machine Learning",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        "location": "Auditorio Principal - Campus Central",
        "max_capacity": 50,
        "status": "ABIERTA"
    }
    res = client.post("/api/v1/events", json=payload, headers=headers)
    assert res.status_code == 201
    event_data = res.json()
    assert event_data["title"] == payload["title"]
    assert event_data["max_capacity"] == 50
    event_id = event_data["id"]

    # Visualizar en la lista de eventos
    res_list = client.get("/api/v1/events")
    assert res_list.status_code == 200
    ids = [e["id"] for e in res_list.json()]
    assert event_id in ids

    # 2. Modificar la información de un evento existente
    update_payload = {"location": "Aula Magna de Ingeniería", "max_capacity": 60}
    res_update = client.put(f"/api/v1/events/{event_id}", json=update_payload, headers=headers)
    assert res_update.status_code == 200
    assert res_update.json()["location"] == "Aula Magna de Ingeniería"
    assert res_update.json()["max_capacity"] == 60


def test_criterio_03_04_05_06_reglas_de_inscripcion(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Crear un evento con capacidad 2
    event_res = client.post("/api/v1/events", json={
        "title": "Taller de FastAPI Avanzado",
        "description": "Taller intensivo práctico de arquitectura",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "location": "Laboratorio 3",
        "max_capacity": 2,
        "status": "ABIERTA"
    }, headers=headers)
    event_id = event_res.json()["id"]

    # 3. Inscribir correctamente a un participante
    p1 = {
        "event_id": event_id,
        "document_id": "87654321",
        "full_name": "Ana Gómez Pérez",
        "email": "ana.gomez@uni.edu",
        "participant_type": "estudiante"
    }
    res_p1 = client.post("/api/v1/registrations", json=p1)
    assert res_p1.status_code == 201
    assert res_p1.json()["status"] == "INSCRITO"
    assert "INS-" in res_p1.json()["code"]

    # 4. Rechazar una inscripción duplicada para el mismo evento
    res_dup = client.post("/api/v1/registrations", json=p1)
    assert res_dup.status_code == 400
    assert "ya se encuentra registrado" in res_dup.json()["detail"]

    # Inscribir segundo participante para llenar cupos (capacidad = 2)
    p2 = {
        "event_id": event_id,
        "document_id": "11223344",
        "full_name": "Carlos Ruiz",
        "email": "carlos.ruiz@uni.edu",
        "participant_type": "docente"
    }
    res_p2 = client.post("/api/v1/registrations", json=p2)
    assert res_p2.status_code == 201

    # 5. Impedir inscripciones cuando se alcance la capacidad máxima
    p3 = {
        "event_id": event_id,
        "document_id": "99887766",
        "full_name": "Lucía Méndez",
        "email": "lucia.mendez@externo.org",
        "participant_type": "externo"
    }
    res_full = client.post("/api/v1/registrations", json=p3)
    assert res_full.status_code == 400
    assert "capacidad máxima" in res_full.json()["detail"]

    # 6. Impedir inscripciones cuando el evento esté cerrado
    # Creamos un evento cerrado
    event_closed_res = client.post("/api/v1/events", json={
        "title": "Conferencia Cerrada",
        "description": "Evento finalizado",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "location": "Auditorio B",
        "max_capacity": 100,
        "status": "CERRADA"
    }, headers=headers)
    closed_id = event_closed_res.json()["id"]

    p4 = {
        "event_id": closed_id,
        "document_id": "55667788",
        "full_name": "Mario Vargas",
        "email": "mario@externo.org",
        "participant_type": "externo"
    }
    res_closed = client.post("/api/v1/registrations", json=p4)
    assert res_closed.status_code == 400
    assert "CERRADAS" in res_closed.json()["detail"]


def test_criterio_07_consultar_y_filtrar_inscripciones(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    ev = client.post("/api/v1/events", json={
        "title": "Seminario de Investigación",
        "description": "Metodología",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "location": "Sala 1",
        "max_capacity": 20,
        "status": "ABIERTA"
    }, headers=headers).json()

    client.post("/api/v1/registrations", json={
        "event_id": ev["id"],
        "document_id": "40404040",
        "full_name": "David Alva",
        "email": "david@uni.edu",
        "participant_type": "estudiante"
    })

    # Filtrar por documento
    res = client.get("/api/v1/registrations?document_id=40404040")
    assert res.status_code == 200
    assert len(res.json()) >= 1
    assert res.json()[0]["full_name"] == "David Alva"

    # Filtrar por evento
    res_ev = client.get(f"/api/v1/registrations?event_id={ev['id']}")
    assert res_ev.status_code == 200
    assert len(res_ev.json()) == 1


def test_criterio_08_09_10_control_de_asistencia(client, admin_token, staff_token):
    admin_hdr = {"Authorization": f"Bearer {admin_token}"}
    staff_hdr = {"Authorization": f"Bearer {staff_token}"}

    ev = client.post("/api/v1/events", json={
        "title": "Congreso de Ingeniería",
        "description": "Conferencias especializadas",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(),
        "location": "Auditorio Central",
        "max_capacity": 30,
        "status": "ABIERTA"
    }, headers=admin_hdr).json()
    event_id = ev["id"]

    # Obtener sesiones (por defecto se crea la sesión 1 obligatoria)
    ev_detail = client.get(f"/api/v1/events/{event_id}").json()
    session_id = ev_detail["sessions"][0]["id"]

    # Inscribir 2 participantes
    reg1 = client.post("/api/v1/registrations", json={
        "event_id": event_id,
        "document_id": "70001111",
        "full_name": "Elena Morales",
        "email": "elena@uni.edu",
        "participant_type": "estudiante"
    }).json()

    reg2 = client.post("/api/v1/registrations", json={
        "event_id": event_id,
        "document_id": "70002222",
        "full_name": "Jorge Ramos",
        "email": "jorge@uni.edu",
        "participant_type": "docente"
    }).json()

    # Cancelar la inscripción de Jorge Ramos
    client.patch(
        f"/api/v1/registrations/{reg2['id']}/status",
        json={"status": "CANCELADO"},
        headers=admin_hdr
    )

    # 8. Registrar correctamente la asistencia a una sesión
    att_res = client.post("/api/v1/attendances", json={
        "session_id": session_id,
        "document_id": "70001111"
    }, headers=staff_hdr)
    assert att_res.status_code == 201
    assert att_res.json()["document_id"] == "70001111"

    # 9. Rechazar registros de asistencia duplicados
    att_dup = client.post("/api/v1/attendances", json={
        "session_id": session_id,
        "document_id": "70001111"
    }, headers=staff_hdr)
    assert att_dup.status_code == 400
    assert "ya fue registrada previamente" in att_dup.json()["detail"]

    # 10. Impedir que una inscripción cancelada registre asistencia
    att_cancelled = client.post("/api/v1/attendances", json={
        "session_id": session_id,
        "document_id": "70002222"
    }, headers=staff_hdr)
    assert att_cancelled.status_code == 400
    assert "CANCELADA" in att_cancelled.json()["detail"]


def test_criterio_11_y_12_certificados_y_pdf(client, admin_token, staff_token):
    admin_hdr = {"Authorization": f"Bearer {admin_token}"}
    staff_hdr = {"Authorization": f"Bearer {staff_token}"}

    ev = client.post("/api/v1/events", json={
        "title": "Seminario de Ciencias de la Computación",
        "description": "Computación Cuántica",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "location": "Auditorio de Ciencias",
        "max_capacity": 50,
        "status": "ABIERTA"
    }, headers=admin_hdr).json()
    event_id = ev["id"]

    # Agregar una segunda sesión obligatoria para validar 100% de asistencia
    session2 = client.post(f"/api/v1/events/{event_id}/sessions", json={
        "title": "Sesión Práctica de Laboratorio",
        "session_date": (datetime.now(timezone.utc) + timedelta(days=1, hours=4)).isoformat(),
        "is_mandatory": True
    }, headers=admin_hdr).json()

    ev_detail = client.get(f"/api/v1/events/{event_id}").json()
    session1_id = ev_detail["sessions"][0]["id"]
    session2_id = session2["id"]

    # Participante A: asistirá a las 2 sesiones
    reg_a = client.post("/api/v1/registrations", json={
        "event_id": event_id,
        "document_id": "90001111",
        "full_name": "Rosa Cáceres",
        "email": "rosa@uni.edu",
        "participant_type": "estudiante"
    }).json()

    # Participante B: asistirá solo a la sesión 1
    reg_b = client.post("/api/v1/registrations", json={
        "event_id": event_id,
        "document_id": "90002222",
        "full_name": "Luis Soto",
        "email": "luis@uni.edu",
        "participant_type": "externo"
    }).json()

    # Registrar asistencias
    client.post("/api/v1/attendances", json={"session_id": session1_id, "document_id": "90001111"}, headers=staff_hdr)
    client.post("/api/v1/attendances", json={"session_id": session2_id, "document_id": "90001111"}, headers=staff_hdr)

    client.post("/api/v1/attendances", json={"session_id": session1_id, "document_id": "90002222"}, headers=staff_hdr)

    # 11. Identificar participantes elegibles y no elegibles para certificados
    elig_res = client.get(f"/api/v1/events/{event_id}/certificates/eligible", headers=admin_hdr)
    assert elig_res.status_code == 200
    data = {p["document_id"]: p["is_eligible"] for p in elig_res.json()}
    assert data["90001111"] is True  # Rosa cumplió 2 de 2
    assert data["90002222"] is False # Luis solo 1 de 2

    # 12. Generar un certificado PDF válido para un participante elegible
    pdf_res = client.get(f"/api/v1/certificates/{reg_a['id']}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")

    # Rechazar PDF para el no elegible
    pdf_reject = client.get(f"/api/v1/certificates/{reg_b['id']}/pdf")
    assert pdf_reject.status_code == 400
    assert "no elegible" in pdf_reject.json()["detail"].lower()


def test_criterio_13_y_15_estadisticas_y_permisos_por_rol(client, admin_token, staff_token):
    admin_hdr = {"Authorization": f"Bearer {admin_token}"}
    staff_hdr = {"Authorization": f"Bearer {staff_token}"}

    # 13. Mostrar estadísticas coherentes en el dashboard
    metrics_res = client.get("/api/v1/dashboard/metrics", headers=admin_hdr)
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert "total_events" in metrics
    assert "open_events" in metrics
    assert "total_registrations" in metrics
    assert "total_attendances" in metrics
    assert "total_eligible_certificates" in metrics

    # 15. Restringir operaciones según los permisos del usuario
    # El personal de registro (staff) NO puede crear eventos (solo admin)
    forbidden_event = client.post("/api/v1/events", json={
        "title": "Evento No Autorizado",
        "description": "Intento de creación por staff",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "location": "Auditorio",
        "max_capacity": 20,
        "status": "ABIERTA"
    }, headers=staff_hdr)
    assert forbidden_event.status_code == 403
    assert "No posee los permisos suficientes" in forbidden_event.json()["detail"]

    # Usuario sin token intentando acceder a métricas
    unauth_metrics = client.get("/api/v1/dashboard/metrics")
    assert unauth_metrics.status_code == 401
