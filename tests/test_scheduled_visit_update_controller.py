"""
Tests para el controlador ScheduledVisitUpdateController
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from flask import Flask
from io import BytesIO
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


class TestScheduledVisitUpdateController:
    """Tests para ScheduledVisitUpdateController"""
    
    @pytest.fixture
    def app(self):
        """Crea una aplicación Flask para testing"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @patch('app.services.scheduled_visit_update_service.ScheduledVisitUpdateService.update_client_visit')
    def test_post_success_without_file(self, mock_update, app):
        """Test actualizar cliente sin archivo"""
        mock_update.return_value = {
            'visit_id': 'visit1',
            'client_id': 'client1',
            'status': 'COMPLETED',
            'find': 'Hallazgos importantes'
        }
        
        with app.test_request_context(
            data={'find': 'Hallazgos importantes'},
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 200
            assert response['success'] is True
            assert response['data']['status'] == 'COMPLETED'
            assert response['data']['find'] == 'Hallazgos importantes'
    
    @patch('app.services.scheduled_visit_update_service.ScheduledVisitUpdateService.update_client_visit')
    def test_post_success_with_file(self, mock_update, app):
        """Test actualizar cliente con archivo"""
        mock_update.return_value = {
            'visit_id': 'visit1',
            'client_id': 'client1',
            'status': 'COMPLETED',
            'find': 'Hallazgos importantes'
        }
        
        # Crear un archivo mock de 1 MB
        file_content = b'x' * (1024 * 1024)  # 1 MB
        
        with app.test_request_context(
            data={
                'find': 'Hallazgos importantes',
                'file': (BytesIO(file_content), 'test.pdf')
            },
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 200
            assert response['success'] is True
    
    def test_post_missing_find(self, app):
        """Test actualizar sin campo find (obligatorio)"""
        with app.test_request_context(
            data={},
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 400
            assert response['success'] is False
            assert 'find' in response['details'].lower()
    
    def test_post_file_too_large(self, app):
        """Test archivo que excede el tamaño máximo"""
        # Crear un archivo mock de 11 MB (excede el límite de 10 MB)
        file_content = b'x' * (11 * 1024 * 1024)
        
        with app.test_request_context(
            data={
                'find': 'Hallazgos importantes',
                'file': (BytesIO(file_content), 'large_file.pdf')
            },
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 400
            assert response['success'] is False
            assert '10 MB' in response['details']
    
    @patch('app.services.scheduled_visit_update_service.ScheduledVisitUpdateService.update_client_visit')
    def test_post_visit_not_found(self, mock_update, app):
        """Test actualizar visita que no existe"""
        mock_update.side_effect = SalesPlanValidationError(
            "No se encontró la visita con ID visit1 para el vendedor seller1"
        )
        
        with app.test_request_context(
            data={'find': 'Hallazgos'},
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 404
            assert response['success'] is False
            assert 'No se encontró la visita' in response['details']
    
    @patch('app.services.scheduled_visit_update_service.ScheduledVisitUpdateService.update_client_visit')
    def test_post_client_not_found(self, mock_update, app):
        """Test actualizar cliente que no existe en la visita"""
        mock_update.side_effect = SalesPlanValidationError(
            "No se encontró el cliente client1 en la visita visit1"
        )
        
        with app.test_request_context(
            data={'find': 'Hallazgos'},
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 404
            assert response['success'] is False
            assert 'No se encontró el cliente' in response['details']
    
    @patch('app.services.scheduled_visit_update_service.ScheduledVisitUpdateService.update_client_visit')
    def test_post_business_logic_error(self, mock_update, app):
        """Test error de lógica de negocio"""
        mock_update.side_effect = SalesPlanBusinessLogicError(
            "Error al actualizar cliente de la visita"
        )
        
        with app.test_request_context(
            data={'find': 'Hallazgos'},
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 500
            assert response['success'] is False
            assert 'Error de lógica de negocio' in response['error']
    
    @patch('app.services.scheduled_visit_update_service.ScheduledVisitUpdateService.update_client_visit')
    def test_post_unexpected_error(self, mock_update, app):
        """Test error inesperado"""
        mock_update.side_effect = Exception("Error inesperado")
        
        with app.test_request_context(
            data={'find': 'Hallazgos'},
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 500
            assert response['success'] is False
            assert 'Error interno del servidor' in response['error']
    
    @patch('app.services.scheduled_visit_update_service.ScheduledVisitUpdateService.update_client_visit')
    def test_post_success_json(self, mock_update, app):
        """Test actualizar cliente con JSON (sin archivo)"""
        mock_update.return_value = {
            'visit_id': 'visit1',
            'client_id': 'client1',
            'status': 'COMPLETED',
            'find': 'Hallazgos importantes'
        }
        
        with app.test_request_context(
            json={'find': 'Hallazgos importantes'},
            content_type='application/json'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 200
            assert response['success'] is True
            assert response['data']['status'] == 'COMPLETED'
            assert response['data']['find'] == 'Hallazgos importantes'
    
    def test_post_missing_find_json(self, app):
        """Test actualizar con JSON sin campo find (obligatorio)"""
        with app.test_request_context(
            json={},
            content_type='application/json'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 400
            assert response['success'] is False
            assert 'find' in response['details'].lower()
    
    def test_post_missing_json_body(self, app):
        """Test actualizar con content-type JSON pero sin body"""
        with app.test_request_context(
            data=None,
            content_type='application/json'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 400
            assert response['success'] is False
            assert 'find' in response['details'].lower()

