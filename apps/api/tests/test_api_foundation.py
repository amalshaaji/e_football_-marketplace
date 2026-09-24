from fastapi.testclient import TestClient

from app.core.errors import DomainError
from app.main import app

client = TestClient(app)


def test_health_and_versioned_api_docs_are_available() -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.headers["x-request-id"]
    assert client.get("/api/v1/openapi.json").status_code == 200


def test_domain_errors_use_the_common_response_envelope() -> None:
    @app.get("/api/v1/test-domain-error", include_in_schema=False)
    def raise_domain_error():
        raise DomainError("invalid_state", "This operation is not allowed.", 409)

    response = client.get("/api/v1/test-domain-error", headers={"X-Request-ID": "request-test"})
    assert response.status_code == 409
    assert response.json() == {
        "error": {"code": "invalid_state", "message": "This operation is not allowed."},
        "request_id": "request-test",
    }
    assert response.headers["x-request-id"] == "request-test"
