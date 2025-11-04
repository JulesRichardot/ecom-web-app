"""
Unit tests for AuthService.

Tests user registration, login, logout, and session management.
"""

import pytest
from main import AuthService, UserRepository, SessionManager


class TestAuthService:
    """Test suite for AuthService."""
    
    def test_register_user_success(self, auth_service):
        """Test successful user registration."""
        user = auth_service.register(
            email="newuser@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            address="123 Main St"
        )
        
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.address == "123 Main St"
        assert user.password_hash is not None
    
    def test_register_duplicate_email(self, auth_service):
        """Test that registering with duplicate email raises ValueError."""
        auth_service.register(
            email="duplicate@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            address="123 Main St"
        )
        
        # Try to register again with same email
        with pytest.raises(ValueError, match="Email déjà utilisé"):
            auth_service.register(
                email="duplicate@example.com",
                password="password456",
                first_name="Jane",
                last_name="Smith",
                address="456 Other St"
            )
    
    def test_login_success(self, auth_service, test_user):
        """Test successful login."""
        token = auth_service.login("test@example.com", "TestPassword123!")
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_login_invalid_email(self, auth_service):
        """Test login with non-existent email raises ValueError."""
        with pytest.raises(ValueError, match="Identifiants invalides"):
            auth_service.login("nonexistent@example.com", "password123")
    
    def test_login_invalid_password(self, auth_service, test_user):
        """Test login with wrong password raises ValueError."""
        with pytest.raises(ValueError, match="Identifiants invalides"):
            auth_service.login("test@example.com", "wrongpassword")
    
    def test_logout(self, auth_service, test_user, sessions):
        """Test logout invalidates session token."""
        token = auth_service.login("test@example.com", "testpassword")
        
        # Verify token is valid
        user_id = sessions.get_user_id(token)
        assert user_id == test_user.id
        
        # Logout
        auth_service.logout(token)
        
        # Verify token is no longer valid
        user_id_after_logout = sessions.get_user_id(token)
        assert user_id_after_logout is None

