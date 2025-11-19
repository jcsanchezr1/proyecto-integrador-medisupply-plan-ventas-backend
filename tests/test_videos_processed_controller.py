"""
Tests para el controlador VideosProcessedController
"""
import pytest
from unittest.mock import Mock, patch
from flask import Flask
from app.controllers.videos_processed_controller import VideosProcessedController


@pytest.fixture
def app():
    """Aplicación Flask para testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


class TestVideosProcessedController:
    """Tests para VideosProcessedController"""
    
    def test_get_success(self, app):
        """Test obtener videos procesados exitosamente"""
        with app.test_request_context():
            controller = VideosProcessedController()
            
            mock_videos = [
                {
                    'id': 1,
                    'visit_id': 'visit-1',
                    'name': 'Cliente Uno',
                    'file_status': 'PROCESSED',
                    'find': 'Encontrado',
                    'filename_url': 'https://example.com/video1.mp4',
                    'filename_url_processed': 'https://example.com/video1_processed.mp4'
                }
            ]
            
            controller.videos_processed_service.get_processed_videos = Mock(
                return_value=(mock_videos, 1)
            )
            
            response, status = controller.get()
            
            assert status == 200
            assert 'data' in response
            assert 'videos' in response['data']
            assert 'pagination' in response['data']
            assert len(response['data']['videos']) == 1
            assert response['data']['pagination']['total'] == 1
            assert response['data']['pagination']['page'] == 1
            assert response['data']['pagination']['per_page'] == 10
    
    def test_get_with_pagination(self, app):
        """Test obtener videos con paginación personalizada"""
        with app.test_request_context('?page=2&per_page=5'):
            controller = VideosProcessedController()
            
            mock_videos = [
                {
                    'id': 6,
                    'visit_id': 'visit-6',
                    'name': 'Cliente Seis',
                    'file_status': 'PROCESSED',
                    'find': None,
                    'filename_url': 'https://example.com/video6.mp4',
                    'filename_url_processed': 'https://example.com/video6_processed.mp4'
                }
            ]
            
            controller.videos_processed_service.get_processed_videos = Mock(
                return_value=(mock_videos, 10)
            )
            
            response, status = controller.get()
            
            assert status == 200
            assert response['data']['pagination']['page'] == 2
            assert response['data']['pagination']['per_page'] == 5
            assert response['data']['pagination']['total'] == 10
            assert response['data']['pagination']['total_pages'] == 2
    
    def test_get_invalid_page(self, app):
        """Test obtener con página inválida"""
        with app.test_request_context('?page=0'):
            controller = VideosProcessedController()
            
            response, status = controller.get()
            
            assert status == 400
            assert 'error' in response
            assert 'El número de página debe ser mayor a 0' in response['details']
    
    def test_get_invalid_per_page_too_large(self, app):
        """Test obtener con per_page muy grande"""
        with app.test_request_context('?per_page=101'):
            controller = VideosProcessedController()
            
            response, status = controller.get()
            
            assert status == 400
            assert 'error' in response
            assert 'El número de resultados por página debe estar entre 1 y 100' in response['details']
    
    def test_get_invalid_per_page_zero(self, app):
        """Test obtener con per_page igual a 0"""
        with app.test_request_context('?per_page=0'):
            controller = VideosProcessedController()
            
            response, status = controller.get()
            
            assert status == 400
            assert 'error' in response
    
    def test_get_invalid_per_page_negative(self, app):
        """Test obtener con per_page negativo"""
        with app.test_request_context('?per_page=-1'):
            controller = VideosProcessedController()
            
            response, status = controller.get()
            
            assert status == 400
            assert 'error' in response
    
    def test_get_empty_results(self, app):
        """Test obtener videos cuando no hay resultados"""
        with app.test_request_context():
            controller = VideosProcessedController()
            
            controller.videos_processed_service.get_processed_videos = Mock(
                return_value=([], 0)
            )
            
            response, status = controller.get()
            
            assert status == 200
            assert len(response['data']['videos']) == 0
            assert response['data']['pagination']['total'] == 0
            assert response['data']['pagination']['total_pages'] == 0
    
    def test_get_service_error(self, app):
        """Test obtener videos cuando hay error en el servicio"""
        with app.test_request_context():
            controller = VideosProcessedController()
            
            controller.videos_processed_service.get_processed_videos = Mock(
                side_effect=Exception("Error de servicio")
            )
            
            response, status = controller.get()
            
            assert status == 500
            assert 'error' in response
            assert 'Error interno del servidor' in response['error']
    
    def test_get_multiple_videos(self, app):
        """Test obtener múltiples videos procesados"""
        with app.test_request_context():
            controller = VideosProcessedController()
            
            mock_videos = [
                {
                    'id': 1,
                    'visit_id': 'visit-1',
                    'name': 'Cliente Uno',
                    'file_status': 'PROCESSED',
                    'find': 'Encontrado',
                    'filename_url': 'https://example.com/video1.mp4',
                    'filename_url_processed': 'https://example.com/video1_processed.mp4'
                },
                {
                    'id': 2,
                    'visit_id': 'visit-2',
                    'name': 'Cliente Dos',
                    'file_status': 'PENDING',
                    'find': None,
                    'filename_url': 'https://example.com/video2.mp4',
                    'filename_url_processed': None
                },
                {
                    'id': 3,
                    'visit_id': 'visit-3',
                    'name': 'Cliente no disponible',
                    'file_status': 'PROCESSED',
                    'find': 'Otro hallazgo',
                    'filename_url': 'https://example.com/video3.mp4',
                    'filename_url_processed': 'https://example.com/video3_processed.mp4'
                }
            ]
            
            controller.videos_processed_service.get_processed_videos = Mock(
                return_value=(mock_videos, 3)
            )
            
            response, status = controller.get()
            
            assert status == 200
            assert len(response['data']['videos']) == 3
            assert response['data']['videos'][0]['name'] == 'Cliente Uno'
            assert response['data']['videos'][1]['name'] == 'Cliente Dos'
            assert response['data']['videos'][2]['name'] == 'Cliente no disponible'
    
    def test_get_pagination_calculation(self, app):
        """Test cálculo correcto de total_pages"""
        with app.test_request_context('?page=1&per_page=3'):
            controller = VideosProcessedController()
            
            mock_videos = [
                {'id': 1, 'visit_id': 'visit-1', 'name': 'Cliente 1', 'file_status': 'PROCESSED', 'find': None, 'filename_url': None, 'filename_url_processed': None},
                {'id': 2, 'visit_id': 'visit-2', 'name': 'Cliente 2', 'file_status': 'PROCESSED', 'find': None, 'filename_url': None, 'filename_url_processed': None},
                {'id': 3, 'visit_id': 'visit-3', 'name': 'Cliente 3', 'file_status': 'PROCESSED', 'find': None, 'filename_url': None, 'filename_url_processed': None}
            ]
            
            controller.videos_processed_service.get_processed_videos = Mock(
                return_value=(mock_videos, 10)
            )
            
            response, status = controller.get()
            
            assert status == 200
            assert response['data']['pagination']['total'] == 10
            assert response['data']['pagination']['total_pages'] == 4  # 10 / 3 = 3.33 -> 4 páginas
    
    def test_get_default_pagination(self, app):
        """Test que los valores por defecto de paginación funcionan"""
        with app.test_request_context():
            controller = VideosProcessedController()
            
            mock_videos = []
            controller.videos_processed_service.get_processed_videos = Mock(
                return_value=(mock_videos, 0)
            )
            
            response, status = controller.get()
            
            assert status == 200
            # Verificar que se llamó con los valores por defecto
            controller.videos_processed_service.get_processed_videos.assert_called_once_with(
                page=1,
                per_page=10
            )

