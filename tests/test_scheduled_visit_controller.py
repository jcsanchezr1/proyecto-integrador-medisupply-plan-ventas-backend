"""
Tests para el controlador ScheduledVisitController
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from flask import Flask
from datetime import date
from app.controllers.scheduled_visit_controller import ScheduledVisitController
from app.models.scheduled_visit import ScheduledVisit, ScheduledVisitClient
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


@pytest.fixture
def app():
    """Aplicación Flask para testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


class TestScheduledVisitController:
    """Tests para ScheduledVisitController"""
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.create_scheduled_visit')
    @patch('app.services.scheduled_visit_service.ScheduledVisitService._validate_seller_exists')
    @patch('app.services.scheduled_visit_service.ScheduledVisitService._validate_client_exists')
    def test_post_success(self, mock_validate_client, mock_validate_seller, mock_create, app):
        """Test crear visita exitosamente"""
        # Configurar mocks
        mock_validate_seller.return_value = True
        mock_validate_client.return_value = True
        
        mock_visit = Mock(spec=ScheduledVisit)
        mock_visit.to_dict.return_value = {
            'id': 'visit1',
            'seller_id': 'seller1',
            'date': '01-12-2025',
            'clients': [
                {'client_id': 'client1'},
                {'client_id': 'client2'}
            ]
        }
        mock_create.return_value = mock_visit
        
        with app.test_request_context(json={
            'date': '01-12-2025',
            'clients': [
                {'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'},
                {'client_id': 'b527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}
            ]
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 201
            assert response['success'] is True
            assert 'data' in response
    
    def test_post_missing_date(self, app):
        """Test crear visita sin fecha"""
        with app.test_request_context(json={
            'clients': [
                {'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}
            ]
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 400
            assert response['success'] is False
            assert 'date' in response['details'].lower()
    
    def test_post_missing_clients(self, app):
        """Test crear visita sin clientes"""
        with app.test_request_context(json={
            'date': '01-12-2025'
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 400
            assert response['success'] is False
            assert 'clients' in response['details'].lower()
    
    def test_post_empty_clients(self, app):
        """Test crear visita con lista de clientes vacía"""
        with app.test_request_context(json={
            'date': '01-12-2025',
            'clients': []
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 400
            assert response['success'] is False
    
    def test_post_clients_not_list(self, app):
        """Test crear visita con clients que no es lista"""
        with app.test_request_context(json={
            'date': '01-12-2025',
            'clients': 'not-a-list'
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 400
            assert response['success'] is False
    
    def test_post_not_json(self, app):
        """Test crear visita sin JSON"""
        with app.test_request_context(data='not json'):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 400
            assert 'JSON' in response['details']
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.create_scheduled_visit')
    def test_post_duplicate_date_seller(self, mock_create, app):
        """Test crear visita con fecha y vendedor duplicados"""
        mock_create.side_effect = SalesPlanValidationError(
            "Ya existe una visita programada para este vendedor en la fecha 01-12-2025"
        )
        
        with app.test_request_context(json={
            'date': '01-12-2025',
            'clients': [
                {'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}
            ]
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 400
            assert response['success'] is False
            assert 'Ya existe una visita programada' in response['details']
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.create_scheduled_visit')
    def test_post_validation_error(self, mock_create, app):
        """Test crear visita con error de validación"""
        mock_create.side_effect = SalesPlanValidationError("Error de validación")
        
        with app.test_request_context(json={
            'date': '01-12-2025',
            'clients': [
                {'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}
            ]
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 400
            assert response['success'] is False
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.create_scheduled_visit')
    def test_post_business_logic_error(self, mock_create, app):
        """Test crear visita con error de lógica de negocio"""
        mock_create.side_effect = SalesPlanBusinessLogicError("Error de negocio")
        
        with app.test_request_context(json={
            'date': '01-12-2025',
            'clients': [
                {'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}
            ]
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 500
            assert response['success'] is False
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.create_scheduled_visit')
    def test_post_unexpected_error(self, mock_create, app):
        """Test crear visita con error inesperado"""
        mock_create.side_effect = Exception("Error inesperado")
        
        with app.test_request_context(json={
            'date': '01-12-2025',
            'clients': [
                {'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}
            ]
        }):
            controller = ScheduledVisitController()
            
            response, status = controller.post('seller1')
            
            assert status == 500
            assert response['success'] is False
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.get_scheduled_visits')
    @patch('app.services.scheduled_visit_service.ScheduledVisitService._validate_seller_exists')
    def test_get_success(self, mock_validate_seller, mock_get_visits, app):
        """Test obtener visitas exitosamente"""
        mock_validate_seller.return_value = True
        mock_get_visits.return_value = [
            {
                'id': 'visit1',
                'date': '01-12-2025',
                'count_clients': 2
            },
            {
                'id': 'visit2',
                'date': '02-12-2025',
                'count_clients': 3
            }
        ]
        
        with app.test_request_context():
            controller = ScheduledVisitController()
            
            response, status = controller.get('seller1')
            
            assert status == 200
            assert response['success'] is True
            assert len(response['data']) == 2
            assert response['data'][0]['count_clients'] == 2
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.get_scheduled_visits')
    @patch('app.services.scheduled_visit_service.ScheduledVisitService._validate_seller_exists')
    def test_get_with_date_filter(self, mock_validate_seller, mock_get_visits, app):
        """Test obtener visitas con filtro de fecha"""
        mock_validate_seller.return_value = True
        mock_get_visits.return_value = [
            {
                'id': 'visit1',
                'date': '01-12-2025',
                'count_clients': 2
            }
        ]
        
        with app.test_request_context(query_string={'date': '01-12-2025'}):
            controller = ScheduledVisitController()
            
            response, status = controller.get('seller1')
            
            assert status == 200
            assert response['success'] is True
            assert len(response['data']) == 1
            mock_get_visits.assert_called_once_with(
                seller_id='seller1',
                visit_date='01-12-2025'
            )
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.get_scheduled_visits')
    @patch('app.services.scheduled_visit_service.ScheduledVisitService._validate_seller_exists')
    def test_get_empty_results(self, mock_validate_seller, mock_get_visits, app):
        """Test obtener visitas sin resultados"""
        mock_validate_seller.return_value = True
        mock_get_visits.return_value = []
        
        with app.test_request_context():
            controller = ScheduledVisitController()
            
            response, status = controller.get('seller1')
            
            assert status == 200
            assert response['success'] is True
            assert len(response['data']) == 0
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.get_scheduled_visits')
    def test_get_validation_error(self, mock_get_visits, app):
        """Test obtener visitas con error de validación"""
        mock_get_visits.side_effect = SalesPlanValidationError("Vendedor no existe")
        
        with app.test_request_context():
            controller = ScheduledVisitController()
            
            response, status = controller.get('seller1')
            
            assert status == 400
            assert response['success'] is False
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.get_scheduled_visits')
    def test_get_business_logic_error(self, mock_get_visits, app):
        """Test obtener visitas con error de lógica de negocio"""
        mock_get_visits.side_effect = SalesPlanBusinessLogicError("Error de negocio")
        
        with app.test_request_context():
            controller = ScheduledVisitController()
            
            response, status = controller.get('seller1')
            
            assert status == 500
            assert response['success'] is False
    
    @patch('app.services.scheduled_visit_service.ScheduledVisitService.get_scheduled_visits')
    def test_get_unexpected_error(self, mock_get_visits, app):
        """Test obtener visitas con error inesperado"""
        mock_get_visits.side_effect = Exception("Error inesperado")
        
        with app.test_request_context():
            controller = ScheduledVisitController()
            
            response, status = controller.get('seller1')
            
            assert status == 500
            assert response['success'] is False

