"""Sprint 2 - Users and Authentication API tests."""
import pytest

from conftest import new_email, register_user, strong_password


@pytest.mark.api
def test_register_empty_body_returns_422_with_field_errors(api):
    """Goal: verify server-side validation on empty registration payload.
    Precondition: none.
    Expected: status 422 with validation errors for email and password."""
    response = api.post("/users/register", data={})
    assert response.status == 422, response.text()
    errors = response.json()
    assert "email" in errors and "password" in errors, errors


@pytest.mark.api
def test_register_leaked_password_is_rejected(api):
    """Goal: verify password policy rejects known leaked passwords.
    Precondition: none.
    Expected: status 422 because 'Welcome01!' appears in known data leaks."""
    response = register_user(api, new_email(), "Welcome01!")
    assert response.status == 422, response.text()
    assert "password" in response.json()


@pytest.mark.api
def test_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    """Goal: verify Bearer token grants access to authenticated user profile.
    Precondition: user registered and token retrieved via auth_headers fixture.
    Expected: status 200 and profile email matches registered user email."""
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]


@pytest.mark.api
def test_register_response_does_not_expose_password(api):
    """Goal: ensure sensitive credentials are never leaked in response payloads.
    Precondition: none.
    Expected: status 201 and 'password' key is absent from response body."""
    response = register_user(api, new_email(), strong_password())
    assert response.status == 201, response.text()
    assert "password" not in response.json()
