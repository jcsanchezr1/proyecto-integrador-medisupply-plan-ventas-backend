"""
Tests para el controlador de health check
"""
import pytest
from app.controllers.health_controller import HealthCheckView


class TestHealthCheckView:
    """Pruebas para HealthCheckView"""
    
    def test_get_method_exists(self):
        """Prueba que el método get existe"""
        assert hasattr(HealthCheckView, 'get')
    
    def test_get_method_signature(self):
        """Prueba la firma del método get"""
        import inspect
        sig = inspect.signature(HealthCheckView.get)
        assert len(sig.parameters) == 1  # Solo self
    
    def test_get_response(self):
        """Prueba la respuesta del método get"""
        view = HealthCheckView()
        response, status_code = view.get()
        
        assert response == "pong"
        assert status_code == 200

