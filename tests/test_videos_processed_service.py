"""
Tests para el servicio VideosProcessedService
"""
import pytest
from unittest.mock import Mock, patch
from app.services.videos_processed_service import VideosProcessedService
from app.repositories.scheduled_visit_repository import ScheduledVisitRepository


class TestVideosProcessedService:
    """Tests para el servicio VideosProcessedService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio"""
        return Mock(spec=ScheduledVisitRepository)
    
    @pytest.fixture
    def service(self, mock_repository):
        """Servicio con repositorio mockeado"""
        return VideosProcessedService(mock_repository)
    
    @pytest.fixture
    def sample_db_clients(self):
        """Datos de muestra de clientes de BD"""
        client1 = Mock()
        client1.id = 1
        client1.visit_id = 'visit-1'
        client1.client_id = 'client-1'
        client1.file_status = 'PROCESSED'
        client1.find = 'Encontrado'
        client1.filename_url = 'https://example.com/video1.mp4'
        client1.filename_url_processed = 'https://example.com/video1_processed.mp4'
        
        client2 = Mock()
        client2.id = 2
        client2.visit_id = 'visit-2'
        client2.client_id = 'client-2'
        client2.file_status = 'PENDING'
        client2.find = None
        client2.filename_url = 'https://example.com/video2.mp4'
        client2.filename_url_processed = None
        
        return [client1, client2]
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_success(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos procesados exitosamente"""
        # Mock del repositorio - devuelve tupla (lista, total)
        mock_repository.get_processed_videos.return_value = (sample_db_clients, 2)
        
        # Mock de las respuestas del servicio de auth
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-1',
                    'name': 'Cliente Uno'
                }
            }
        }
        
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-2',
                    'name': 'Cliente Dos'
                }
            }
        }
        
        mock_get.side_effect = [mock_response1, mock_response2]
        
        # Ejecutar
        videos, total = service.get_processed_videos()
        
        # Verificar
        assert len(videos) == 2
        assert total == 2
        assert videos[0]['id'] == 1
        assert videos[0]['visit_id'] == 'visit-1'
        assert videos[0]['name'] == 'Cliente Uno'
        assert videos[0]['file_status'] == 'PROCESSED'
        assert videos[0]['find'] == 'Encontrado'
        assert videos[0]['filename_url'] == 'https://example.com/video1.mp4'
        assert videos[0]['filename_url_processed'] == 'https://example.com/video1_processed.mp4'
        
        assert videos[1]['id'] == 2
        assert videos[1]['visit_id'] == 'visit-2'
        assert videos[1]['name'] == 'Cliente Dos'
        assert videos[1]['file_status'] == 'PENDING'
        assert videos[1]['find'] is None
        assert videos[1]['filename_url'] == 'https://example.com/video2.mp4'
        assert videos[1]['filename_url_processed'] is None
        
        mock_repository.get_processed_videos.assert_called_once_with(
            page=1, per_page=10, visit_id=None, client_ids=None, file_status=None, find=None
        )
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_client_not_available(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos cuando el cliente no está disponible"""
        # Mock del repositorio - devuelve tupla (lista, total)
        mock_repository.get_processed_videos.return_value = (sample_db_clients, 2)
        
        # Mock de respuestas del servicio de auth - cliente no encontrado
        mock_response1 = Mock()
        mock_response1.status_code = 404
        
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-2',
                    'name': 'Cliente Dos'
                }
            }
        }
        
        mock_get.side_effect = [mock_response1, mock_response2]
        
        # Ejecutar
        videos, total = service.get_processed_videos()
        
        # Verificar
        assert len(videos) == 2
        assert total == 2
        assert videos[0]['name'] == 'Cliente no disponible'
        assert videos[1]['name'] == 'Cliente Dos'
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_request_exception(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos cuando hay excepción al consultar el servicio de auth"""
        import requests
        
        # Mock del repositorio - devuelve tupla (lista, total)
        mock_repository.get_processed_videos.return_value = (sample_db_clients, 2)
        
        # Mock de excepción en requests
        mock_get.side_effect = requests.exceptions.RequestException("Error de conexión")
        
        # Ejecutar
        videos, total = service.get_processed_videos()
        
        # Verificar que devuelve "Cliente no disponible" cuando hay error
        assert len(videos) == 2
        assert total == 2
        assert videos[0]['name'] == 'Cliente no disponible'
        assert videos[1]['name'] == 'Cliente no disponible'
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_empty_list(self, mock_get, service, mock_repository):
        """Test obtener videos cuando no hay registros"""
        # Mock del repositorio - tupla con lista vacía y total 0
        mock_repository.get_processed_videos.return_value = ([], 0)
        
        # Ejecutar
        videos, total = service.get_processed_videos()
        
        # Verificar
        assert len(videos) == 0
        assert total == 0
        mock_repository.get_processed_videos.assert_called_once_with(
            page=1, per_page=10, visit_id=None, client_ids=None, file_status=None, find=None
        )
        mock_get.assert_not_called()
    
    def test_get_processed_videos_repository_error(self, service, mock_repository):
        """Test obtener videos cuando hay error en el repositorio"""
        # Mock del repositorio con error
        mock_repository.get_processed_videos.side_effect = Exception("Error de BD")
        
        # Ejecutar y verificar que lanza excepción
        with pytest.raises(Exception, match="Error al obtener videos procesados"):
            service.get_processed_videos()
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_client_name_success_user_wrapped(self, mock_get, service):
        """Test obtener nombre de cliente cuando viene envuelto en data.user"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-1',
                    'name': 'Cliente Test'
                }
            }
        }
        mock_get.return_value = mock_response
        
        name = service._get_client_name('client-1')
        
        assert name == 'Cliente Test'
        mock_get.assert_called_once()
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_client_name_success_flat_data(self, mock_get, service):
        """Test obtener nombre de cliente cuando viene directo en data"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'id': 'client-1',
                'name': 'Cliente Plano'
            }
        }
        mock_get.return_value = mock_response
        
        name = service._get_client_name('client-1')
        
        assert name == 'Cliente Plano'
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_client_name_not_found(self, mock_get, service):
        """Test obtener nombre de cliente cuando no se encuentra (404)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        name = service._get_client_name('client-1')
        
        assert name is None
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_client_name_request_exception(self, mock_get, service):
        """Test obtener nombre de cliente cuando hay excepción de requests"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Error de conexión")
        
        name = service._get_client_name('client-1')
        
        assert name is None
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_with_pagination(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos procesados con parámetros de paginación"""
        # Mock del repositorio - devuelve tupla (lista, total)
        mock_repository.get_processed_videos.return_value = (sample_db_clients, 10)
        
        # Mock de las respuestas del servicio de auth
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-1',
                    'name': 'Cliente Uno'
                }
            }
        }
        
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-2',
                    'name': 'Cliente Dos'
                }
            }
        }
        
        mock_get.side_effect = [mock_response1, mock_response2]
        
        # Ejecutar con parámetros de paginación
        videos, total = service.get_processed_videos(page=2, per_page=5)
        
        # Verificar
        assert len(videos) == 2
        assert total == 10
        mock_repository.get_processed_videos.assert_called_once_with(
            page=2, per_page=5, visit_id=None, client_ids=None, file_status=None, find=None
        )
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_with_visit_id_filter(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos procesados con filtro por visit_id"""
        # Mock del repositorio - devuelve tupla (lista, total)
        mock_repository.get_processed_videos.return_value = (sample_db_clients[:1], 1)
        
        # Mock de respuesta del servicio de auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-1',
                    'name': 'Cliente Uno'
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Ejecutar con filtro por visit_id
        videos, total = service.get_processed_videos(visit_id='visit-1')
        
        # Verificar
        assert len(videos) == 1
        assert total == 1
        mock_repository.get_processed_videos.assert_called_once_with(
            page=1, per_page=10, visit_id='visit-1', client_ids=None, file_status=None, find=None
        )
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_with_client_name_filter(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos procesados con filtro por nombre de cliente"""
        # Mock de búsqueda de clientes por nombre
        mock_response_search = Mock()
        mock_response_search.status_code = 200
        mock_response_search.json.return_value = {
            'data': {
                'users': [
                    {'id': 'client-1'},
                    {'id': 'client-2'}
                ]
            }
        }
        
        # Mock de obtención de nombres de clientes
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-1',
                    'name': 'Cliente Uno'
                }
            }
        }
        
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-2',
                    'name': 'Cliente Dos'
                }
            }
        }
        
        mock_get.side_effect = [mock_response_search, mock_response1, mock_response2]
        
        # Mock del repositorio
        mock_repository.get_processed_videos.return_value = (sample_db_clients, 2)
        
        # Ejecutar con filtro por nombre de cliente
        videos, total = service.get_processed_videos(client_name='Cliente')
        
        # Verificar
        assert len(videos) == 2
        assert total == 2
        mock_repository.get_processed_videos.assert_called_once_with(
            page=1, per_page=10, visit_id=None, client_ids=['client-1', 'client-2'], file_status=None, find=None
        )
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_with_client_name_filter_no_results(self, mock_get, service, mock_repository):
        """Test obtener videos cuando el filtro por nombre de cliente no encuentra clientes"""
        # Mock de búsqueda de clientes por nombre - sin resultados
        mock_response_search = Mock()
        mock_response_search.status_code = 200
        mock_response_search.json.return_value = {
            'data': {
                'users': []
            }
        }
        mock_get.return_value = mock_response_search
        
        # Ejecutar con filtro por nombre de cliente que no existe
        videos, total = service.get_processed_videos(client_name='Cliente Inexistente')
        
        # Verificar que retorna lista vacía sin llamar al repositorio
        assert len(videos) == 0
        assert total == 0
        mock_repository.get_processed_videos.assert_not_called()
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_with_file_status_filter(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos procesados con filtro por file_status"""
        # Mock del repositorio - devuelve solo videos procesados
        mock_repository.get_processed_videos.return_value = (sample_db_clients[:1], 1)
        
        # Mock de respuesta del servicio de auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-1',
                    'name': 'Cliente Uno'
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Ejecutar con filtro por file_status
        videos, total = service.get_processed_videos(file_status='PROCESSED')
        
        # Verificar
        assert len(videos) == 1
        assert total == 1
        mock_repository.get_processed_videos.assert_called_once_with(
            page=1, per_page=10, visit_id=None, client_ids=None, file_status='PROCESSED', find=None
        )
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_with_find_filter(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos procesados con filtro por find"""
        # Mock del repositorio - devuelve solo videos con find
        mock_repository.get_processed_videos.return_value = (sample_db_clients[:1], 1)
        
        # Mock de respuesta del servicio de auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-1',
                    'name': 'Cliente Uno'
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Ejecutar con filtro por find
        videos, total = service.get_processed_videos(find='Encontrado')
        
        # Verificar
        assert len(videos) == 1
        assert total == 1
        mock_repository.get_processed_videos.assert_called_once_with(
            page=1, per_page=10, visit_id=None, client_ids=None, file_status=None, find='Encontrado'
        )
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_processed_videos_with_multiple_filters(self, mock_get, service, mock_repository, sample_db_clients):
        """Test obtener videos procesados con múltiples filtros"""
        # Mock del repositorio
        mock_repository.get_processed_videos.return_value = (sample_db_clients[:1], 1)
        
        # Mock de respuesta del servicio de auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'user': {
                    'id': 'client-1',
                    'name': 'Cliente Uno'
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Ejecutar con múltiples filtros
        videos, total = service.get_processed_videos(
            visit_id='visit-1',
            file_status='PROCESSED',
            find='Encontrado'
        )
        
        # Verificar
        assert len(videos) == 1
        assert total == 1
        mock_repository.get_processed_videos.assert_called_once_with(
            page=1, per_page=10, visit_id='visit-1', client_ids=None, file_status='PROCESSED', find='Encontrado'
        )
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_client_ids_by_name_success(self, mock_get, service):
        """Test obtener IDs de clientes por nombre"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'users': [
                    {'id': 'client-1'},
                    {'id': 'client-2'}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        client_ids = service._get_client_ids_by_name('Cliente')
        
        assert client_ids == ['client-1', 'client-2']
        mock_get.assert_called_once()
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_client_ids_by_name_empty(self, mock_get, service):
        """Test obtener IDs de clientes cuando no hay resultados"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'users': []
            }
        }
        mock_get.return_value = mock_response
        
        client_ids = service._get_client_ids_by_name('Inexistente')
        
        assert client_ids == []
    
    @patch('app.services.videos_processed_service.requests.get')
    def test_get_client_ids_by_name_request_exception(self, mock_get, service):
        """Test obtener IDs de clientes cuando hay excepción"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Error de conexión")
        
        client_ids = service._get_client_ids_by_name('Cliente')
        
        assert client_ids == []

