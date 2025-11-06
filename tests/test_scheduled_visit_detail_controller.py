"""
Tests para el controlador ScheduledVisitDetailController
"""
import pytest
from unittest.mock import patch, Mock
from flask import Flask
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


class TestScheduledVisitDetailController:
    """Tests para ScheduledVisitDetailController"""
    
    @pytest.fixture
    def app(self):
        """Crea una aplicación Flask para testing"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @patch('app.services.scheduled_visit_detail_service.ScheduledVisitDetailService.get_visit_detail')
    def test_get_success(self, mock_get_visit_detail, app):
        """Test obtener detalle de visita exitosamente"""
        mock_get_visit_detail.return_value = {
            'id': 'visit1',
            'seller_id': 'seller1',
            'date': '01-12-2025',
            'clients': [
                {
                    'id': 'client1',
                    'name': 'Hospital General',
                    'email': 'test@example.com'
                }
            ],
            'created_at': '2025-11-01T10:00:00',
            'updated_at': '2025-11-01T10:00:00'
        }
        
        with app.test_request_context():
            from app.controllers.scheduled_visit_detail_controller import ScheduledVisitDetailController
            controller = ScheduledVisitDetailController()
            
            response, status = controller.get('seller1', 'visit1')
            
            assert status == 200
            assert response['success'] is True
            assert response['data']['id'] == 'visit1'
            assert len(response['data']['clients']) == 1
            assert response['message'] == 'Detalle de visita obtenido exitosamente'
    
    @patch('app.services.scheduled_visit_detail_service.ScheduledVisitDetailService.get_visit_detail')
    def test_get_visit_not_found(self, mock_get_visit_detail, app):
        """Test obtener detalle de visita que no existe"""
        mock_get_visit_detail.side_effect = SalesPlanValidationError(
            "No se encontró la visita con ID visit1 para el vendedor seller1"
        )
        
        with app.test_request_context():
            from app.controllers.scheduled_visit_detail_controller import ScheduledVisitDetailController
            controller = ScheduledVisitDetailController()
            
            response, status = controller.get('seller1', 'visit1')
            
            assert status == 404
            assert response['success'] is False
            assert 'No se encontró la visita' in response['details']
    
    @patch('app.services.scheduled_visit_detail_service.ScheduledVisitDetailService.get_visit_detail')
    def test_get_seller_not_found(self, mock_get_visit_detail, app):
        """Test obtener detalle con vendedor que no existe"""
        mock_get_visit_detail.side_effect = SalesPlanValidationError(
            "El vendedor con ID seller1 no existe"
        )
        
        with app.test_request_context():
            from app.controllers.scheduled_visit_detail_controller import ScheduledVisitDetailController
            controller = ScheduledVisitDetailController()
            
            response, status = controller.get('seller1', 'visit1')
            
            assert status == 404
            assert response['success'] is False
            assert 'El vendedor con ID seller1 no existe' in response['details']
    
    @patch('app.services.scheduled_visit_detail_service.ScheduledVisitDetailService.get_visit_detail')
    def test_get_business_logic_error(self, mock_get_visit_detail, app):
        """Test error de lógica de negocio"""
        mock_get_visit_detail.side_effect = SalesPlanBusinessLogicError(
            "Error al obtener detalle de visita"
        )
        
        with app.test_request_context():
            from app.controllers.scheduled_visit_detail_controller import ScheduledVisitDetailController
            controller = ScheduledVisitDetailController()
            
            response, status = controller.get('seller1', 'visit1')
            
            assert status == 500
            assert response['success'] is False
            assert 'Error de lógica de negocio' in response['error']
    
    @patch('app.services.scheduled_visit_detail_service.ScheduledVisitDetailService.get_visit_detail')
    def test_get_unexpected_error(self, mock_get_visit_detail, app):
        """Test error inesperado"""
        mock_get_visit_detail.side_effect = Exception("Error inesperado")
        
        with app.test_request_context():
            from app.controllers.scheduled_visit_detail_controller import ScheduledVisitDetailController
            controller = ScheduledVisitDetailController()
            
            response, status = controller.get('seller1', 'visit1')
            
            assert status == 500
            assert response['success'] is False
            assert 'Error interno del servidor' in response['error']
    
    @patch('app.services.scheduled_visit_detail_service.ScheduledVisitDetailService.get_visit_detail')
    def test_get_with_multiple_clients(self, mock_get_visit_detail, app):
        """Test obtener detalle de visita con múltiples clientes"""
        mock_get_visit_detail.return_value = {
            'id': 'visit1',
            'seller_id': 'seller1',
            'date': '01-12-2025',
            'clients': [
                {
                    'id': 'client1',
                    'name': 'Hospital General',
                    'tax_id': '123456789',
                    'email': 'hospital1@example.com',
                    'address': 'Calle 123',
                    'phone': '1234567890',
                    'institution_type': 'Hospital',
                    'enabled': True
                },
                {
                    'id': 'client2',
                    'name': 'Clínica Central',
                    'tax_id': '987654321',
                    'email': 'clinica@example.com',
                    'address': 'Avenida 456',
                    'phone': '0987654321',
                    'institution_type': 'Clínica',
                    'enabled': True
                }
            ],
            'created_at': '2025-11-01T10:00:00',
            'updated_at': '2025-11-01T10:00:00'
        }
        
        with app.test_request_context():
            from app.controllers.scheduled_visit_detail_controller import ScheduledVisitDetailController
            controller = ScheduledVisitDetailController()
            
            response, status = controller.get('seller1', 'visit1')
            
            assert status == 200
            assert response['success'] is True
            assert len(response['data']['clients']) == 2
            assert response['data']['clients'][0]['name'] == 'Hospital General'
            assert response['data']['clients'][1]['name'] == 'Clínica Central'

