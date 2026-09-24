import pytest
from pydantic import ValidationError

from app.auth.schemas import LoginRequest, RegisterRequest


def test_registration_normalizes_email_and_validates_password() -> None:
    payload = RegisterRequest(email=" Person@Example.com ", password="secure-password", display_name="Player")
    assert payload.email == "person@example.com"
    with pytest.raises(ValidationError):
        RegisterRequest(email="bad", password="tiny", display_name="Player")


def test_login_rejects_malformed_email() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="bad", password="anything")
