from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.database.models import UserRole
from app.main import app


def test_admin_routes_require_authentication() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/admin/stats")
    assert response.status_code == 401


def test_non_admin_role_is_forbidden(monkeypatch) -> None:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role=UserRole.BUYER)
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/admin/stats")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    assert response.status_code == 403
