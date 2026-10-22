import yaml
from pathlib import Path

def test_openapi_contract_file_exists_and_valid():
    specs_path = Path(__file__).resolve().parent.parent.parent.parent / "specs" / "contracts" / "openapi.yaml"
    assert specs_path.exists(), "El archivo de contrato openapi.yaml debe existir"

    with open(specs_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    assert spec["openapi"] == "3.0.3"
    assert "paths" in spec
    assert "/api/v1/events" in spec["paths"]
    assert "/api/v1/registrations" in spec["paths"]
    assert "/api/v1/attendances" in spec["paths"]
    assert "/api/v1/certificates/{registration_id}/pdf" in spec["paths"]
    assert "/api/v1/dashboard/metrics" in spec["paths"]

def test_fastapi_schema_conformance(client):
    res = client.get("/openapi.json")
    assert res.status_code == 200
    fastapi_spec = res.json()

    # Verificar que las rutas clave del contrato estén presentes en la aplicación FastAPI
    paths = fastapi_spec["paths"]
    assert "/api/v1/events" in paths
    assert "/api/v1/registrations" in paths
    assert "/api/v1/attendances" in paths
    assert "/api/v1/certificates/{registration_id}/pdf" in paths
    assert "/api/v1/dashboard/metrics" in paths
