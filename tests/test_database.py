"""
Tests para database.py
"""
import pytest
from unittest.mock import MagicMock, patch
from app.config.database import SessionLocal, auto_close_session


class TestDatabase:
    """Tests para configuración de base de datos"""
    
    def test_session_local_creation(self):
        """Test: Creación de SessionLocal"""
        assert SessionLocal is not None
        assert hasattr(SessionLocal, '__call__')
    
    def test_auto_close_session_decorator_success(self):
        """Test: Decorador auto_close_session con éxito"""
        mock_session = MagicMock()
        mock_session.in_transaction.return_value = False
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
            
            @auto_close_session
            def test_method(self):
                return "success"
        
        controller = TestController()
        
        with patch('app.config.database.SessionLocal', return_value=mock_session):
            result = controller.test_method()
        
        assert result == "success"
    
    def test_auto_close_session_decorator_with_exception(self):
        """Test: Decorador auto_close_session con excepción"""
        mock_session = MagicMock()
        mock_session.in_transaction.return_value = False
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
            
            @auto_close_session
            def test_method(self):
                raise ValueError("Test error")
        
        controller = TestController()
        
        with patch('app.config.database.SessionLocal', return_value=mock_session):
            with pytest.raises(ValueError, match="Test error"):
                controller.test_method()
    
    def test_auto_close_session_with_mocked_service(self):
        """Test: Decorador con servicio mockeado"""
        class TestController:
            def __init__(self):
                self.order_service = MagicMock()
                self.order_service.__class__.__module__ = 'test.mock'
                self.order_service.__class__.__name__ = 'MockService'
            
            @auto_close_session
            def test_method(self):
                return "success"
        
        controller = TestController()
        result = controller.test_method()
        
        assert result == "success"
    
    def test_auto_close_session_commits_transaction(self):
        """Test: Decorador hace commit de transacción"""
        mock_session = MagicMock()
        mock_session.in_transaction.return_value = True
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
            
            @auto_close_session
            def test_method(self):
                return "success"
        
        controller = TestController()
        
        with patch('app.config.database.SessionLocal', return_value=mock_session):
            controller.test_method()
        
        mock_session.commit.assert_called()
    
    def test_auto_close_session_rollback_on_error(self):
        """Test: Decorador hace rollback en error"""
        mock_session = MagicMock()
        mock_session.in_transaction.return_value = True
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
            
            @auto_close_session
            def test_method(self):
                raise ValueError("Test error")
        
        controller = TestController()
        
        with patch('app.config.database.SessionLocal', return_value=mock_session):
            with pytest.raises(ValueError):
                controller.test_method()
        
        mock_session.rollback.assert_called()
    
    def test_auto_close_session_refresh_on_commit(self):
        """Test: Decorador hace refresh después de commit"""
        mock_session = MagicMock()
        mock_session.in_transaction.return_value = True
        mock_added_entity = MagicMock()
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
                self.order_repository.session = mock_session
            
            @auto_close_session
            def test_method(self):
                mock_session.add(mock_added_entity)
                return mock_added_entity
        
        controller = TestController()
        
        with patch('app.config.database.SessionLocal', return_value=mock_session):
            controller.test_method()
        
        mock_session.commit.assert_called()
    
    def test_auto_close_session_rollback_exception(self):
        """Test: Decorador con excepción en rollback (línea 103-104)"""
        mock_session = MagicMock()
        mock_session.in_transaction.return_value = True
        mock_session.rollback.side_effect = Exception("Rollback error")
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
            
            @auto_close_session
            def test_method(self):
                raise ValueError("Test error")
        
        controller = TestController()
        
        with patch('app.config.database.SessionLocal', return_value=mock_session):
            with pytest.raises(ValueError):
                controller.test_method()
    
    def test_auto_close_session_close_exception(self):
        """Test: Decorador con excepción en close (línea 120-121)"""
        mock_session = MagicMock()
        mock_session.in_transaction.return_value = False
        mock_session.close.side_effect = Exception("Close error")
        
        class TestController:
            def __init__(self):
                self.order_repository = MagicMock()
            
            @auto_close_session
            def test_method(self):
                return "success"
        
        controller = TestController()
        
        with patch('app.config.database.SessionLocal', return_value=mock_session):
            result = controller.test_method()
            assert result == "success"

