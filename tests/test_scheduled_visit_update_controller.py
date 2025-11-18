"""
Tests para el controlador ScheduledVisitUpdateController
"""
import pytest
import sys
from unittest.mock import patch, Mock, MagicMock
from flask import Flask
from io import BytesIO
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


# Mock de CloudStorageService para evitar conflictos de importación con google.cloud
class MockCloudStorageService:
    def __init__(self, config=None):
        pass
    
    def upload_file(self, file, filename):
        return True, "Archivo subido exitosamente", "https://storage.googleapis.com/bucket/file.mp4"


# Mock de PubSubService para evitar conflictos de importación con google.cloud
class MockPubSubService:
    def __init__(self, config=None):
        pass
    
    def publish_video_processing_event(self, scheduled_visit_client_id):
        return "mock-message-id-12345"


# Aplicar el mock antes de importar el controlador
sys.modules['app.services.cloud_storage_service'] = Mock()
sys.modules['app.services.cloud_storage_service'].CloudStorageService = MockCloudStorageService
sys.modules['app.services.pubsub_service'] = Mock()
sys.modules['app.services.pubsub_service'].PubSubService = MockPubSubService


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
        """Test actualizar cliente con archivo MP4"""
        mock_update.return_value = {
            'visit_id': 'visit1',
            'client_id': 'client1',
            'status': 'COMPLETED',
            'find': 'Hallazgos importantes',
            'filename': 'visit1_client1_abc123.mp4',
            'filename_url': 'https://storage.googleapis.com/bucket/file.mp4',
            'file_status': 'Cargado'
        }
        
        # Crear un archivo mock de 1 MB
        file_content = b'x' * (1024 * 1024)  # 1 MB
        
        with app.test_request_context(
            data={
                'find': 'Hallazgos importantes',
                'file': (BytesIO(file_content), 'test.mp4')
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
        # Crear un archivo mock de 501 MB (excede el límite de 500 MB)
        file_content = b'x' * (501 * 1024 * 1024)
        
        with app.test_request_context(
            data={
                'find': 'Hallazgos importantes',
                'file': (BytesIO(file_content), 'large_file.mp4')
            },
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 400
            assert response['success'] is False
            assert '500 MB' in response['details']
    
    def test_post_file_invalid_extension_pdf(self, app):
        """Test archivo con extensión PDF (no permitida)"""
        # Crear un archivo mock de 1 MB
        file_content = b'x' * (1024 * 1024)
        
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
            
            assert status == 400
            assert response['success'] is False
            assert 'MP4' in response['details']
            assert 'pdf' in response['details']
    
    def test_post_file_invalid_extension_avi(self, app):
        """Test archivo con extensión AVI (no permitida)"""
        # Crear un archivo mock de 1 MB
        file_content = b'x' * (1024 * 1024)
        
        with app.test_request_context(
            data={
                'find': 'Hallazgos importantes',
                'file': (BytesIO(file_content), 'test.avi')
            },
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 400
            assert response['success'] is False
            assert 'MP4' in response['details']
            assert 'avi' in response['details']
    
    def test_post_file_no_extension(self, app):
        """Test archivo sin extensión"""
        # Crear un archivo mock de 1 MB
        file_content = b'x' * (1024 * 1024)
        
        with app.test_request_context(
            data={
                'find': 'Hallazgos importantes',
                'file': (BytesIO(file_content), 'testvideo')
            },
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 400
            assert response['success'] is False
            assert 'MP4' in response['details']
            assert 'sin extensión' in response['details']
    
    @patch('app.services.scheduled_visit_update_service.ScheduledVisitUpdateService.update_client_visit')
    def test_post_file_upload_fails(self, mock_update, app):
        """Test cuando falla la subida del archivo a Cloud Storage"""
        from app.exceptions.custom_exceptions import SalesPlanBusinessLogicError
        
        # El servicio lanza excepción cuando falla la subida
        mock_update.side_effect = SalesPlanBusinessLogicError("Error al subir archivo: Error de Cloud Storage")
        
        # Crear un archivo mock de 1 MB
        file_content = b'x' * (1024 * 1024)
        
        with app.test_request_context(
            data={
                'find': 'Hallazgos importantes',
                'file': (BytesIO(file_content), 'test.mp4')
            },
            content_type='multipart/form-data'
        ):
            from app.controllers.scheduled_visit_update_controller import ScheduledVisitUpdateController
            controller = ScheduledVisitUpdateController()
            
            response, status = controller.post('seller1', 'visit1', 'client1')
            
            assert status == 500
            assert response['success'] is False
            assert 'Error al subir archivo' in response['details']
    
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

