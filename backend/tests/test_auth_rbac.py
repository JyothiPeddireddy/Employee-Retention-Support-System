"""Comprehensive tests for Authentication, JWT tokens, and RBAC authorization."""
import pytest
from datetime import date
from fastapi import HTTPException
from backend.app.models.app_user import AppUser, UserRole
from backend.app.schemas.auth import UserRegisterRequest, UserLoginRequest, ChangePasswordRequest
from backend.app.services.auth_service import AuthService
from backend.app.core.security import decode_access_token, verify_password
from backend.app.core.dependencies import check_employee_access, require_roles
from backend.tests.conftest import get_token_for


def test_user_registration_and_password_hashing(db_session):
    """Test user registration with bcrypt password hashing and unique constraints."""
    req = UserRegisterRequest(
        username="new_user_1",
        email="new.user@company.internal",
        password="SecurePassword123!",
        role=UserRole.EMPLOYEE
    )
    user = AuthService.register_user(db=db_session, req=req)

    assert user.user_id.startswith("USR-")
    assert user.username == "new_user_1"
    assert user.email == "new.user@company.internal"
    assert verify_password("SecurePassword123!", user.hashed_password)
    assert user.is_active is True

    # Duplicate username rejection
    with pytest.raises(HTTPException) as exc_info:
        AuthService.register_user(db=db_session, req=req)
    assert exc_info.value.status_code == 400
    assert "already registered" in exc_info.value.detail


def test_user_authentication_and_jwt_lifecycle(db_session):
    """Test login, token generation, decoding, password change, and token revocation on logout."""
    req = UserRegisterRequest(
        username="auth_tester",
        email="auth.tester@company.internal",
        password="OriginalPassword123!",
        role=UserRole.MANAGER
    )
    user = AuthService.register_user(db=db_session, req=req)

    # 1. Successful authentication
    authenticated = AuthService.authenticate(
        db=db_session,
        username="auth_tester",
        password="OriginalPassword123!"
    )
    assert authenticated is not None
    assert authenticated.user_id == user.user_id

    # 2. Failed authentication with wrong password
    failed = AuthService.authenticate(
        db=db_session,
        username="auth_tester",
        password="WrongPassword999!"
    )
    assert failed is None

    # 3. Change password
    change_req = ChangePasswordRequest(
        current_password="OriginalPassword123!",
        new_password="NewSecretPassword456!"
    )
    AuthService.change_password(db=db_session, user=user, req=change_req)

    # Verify new password works
    auth_new = AuthService.authenticate(
        db=db_session,
        username="auth_tester",
        password="NewSecretPassword456!"
    )
    assert auth_new is not None

    # 4. JWT token generation and revocation
    token = get_token_for("auth_tester", UserRole.MANAGER.value, user.user_id)["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "auth_tester"

    # Revoke token on logout
    AuthService.logout(token)
    assert decode_access_token(token) is None


def test_rbac_role_checker_enforcement():
    """Test RBAC role checker dependency."""
    admin_user = AppUser(user_id="USR-01", username="admin", role=UserRole.ADMIN.value, is_active=True)
    hr_user = AppUser(user_id="USR-02", username="hr", role=UserRole.HR_PARTNER.value, is_active=True)
    emp_user = AppUser(user_id="USR-03", username="emp", role=UserRole.EMPLOYEE.value, is_active=True)

    checker = require_roles(UserRole.HR_PARTNER)

    # HR Partner allowed
    assert checker(current_user=hr_user) == hr_user

    # Admin always allowed
    assert checker(current_user=admin_user) == admin_user

    # Employee rejected with 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=emp_user)
    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail


def test_resource_level_access_scoping(db_session, seeded_db):
    """Test employee and manager resource-level permission scoping."""
    hr_user = AppUser(user_id="USR-01", username="hr", role=UserRole.HR_PARTNER.value, is_active=True)
    emp_user = AppUser(user_id="USR-02", username="emp", role=UserRole.EMPLOYEE.value, employee_id="EMP-000002", is_active=True)
    mgr_user = AppUser(user_id="USR-03", username="mgr", role=UserRole.MANAGER.value, employee_id="EMP-000001", is_active=True)

    # HR can access any employee
    assert check_employee_access(current_user=hr_user, target_employee_id="EMP-000002", db=db_session) is True

    # Employee can access self
    assert check_employee_access(current_user=emp_user, target_employee_id="EMP-000002", db=db_session) is True

    # Employee cannot access another employee's record
    with pytest.raises(HTTPException) as exc_info:
        check_employee_access(current_user=emp_user, target_employee_id="EMP-000001", db=db_session)
    assert exc_info.value.status_code == 403
    assert "own records" in exc_info.value.detail
