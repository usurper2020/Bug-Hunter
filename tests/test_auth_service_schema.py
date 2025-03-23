import pytest
from unittest.mock import MagicMock
from app.auth.auth_service import AuthService

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    return MagicMock()

def test_register_user_with_schema(mock_db_session):
    """Test the user registration functionality with schema validation."""
    auth_service = AuthService(mock_db_session)
    
    # Mock the methods used in the registration process
    mock_db_session.cursor.return_value.__enter__.return_value = MagicMock()
    
    # Simulate the behavior of fetchone to return a count of 0
    mock_db_session.cursor.return_value.__enter__.return_value.fetchone.return_value = [0]
    
    # Simulate user registration
    username = "testuser"
    password = "testpassword"
    email = "testuser@example.com"
    
    # Call the register_user method
    result = auth_service.register_user(username, password, email=email)
    
    # Assert that the registration was successful
    assert result is True
    mock_db_session.cursor.return_value.__enter__.return_value.execute.assert_called()