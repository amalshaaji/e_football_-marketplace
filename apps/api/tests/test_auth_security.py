import uuid

from app.auth.security import create_token, decode_token, hash_password, verify_password


def test_password_hash_is_salted_and_verified() -> None:
    first = hash_password("a long test password")
    second = hash_password("a long test password")
    assert first != second
    assert verify_password("a long test password", first)
    assert not verify_password("incorrect", first)


def test_tokens_are_signed_and_token_type_is_checked() -> None:
    token = create_token(uuid.uuid4(), "BUYER", token_type="access", expires_in=60)
    assert decode_token(token)["role"] == "BUYER"
    try:
        decode_token(token, expected_type="refresh")
    except ValueError:
        pass
    else:
        raise AssertionError("access token was accepted as refresh token")
