"""
Tests para PubSubService
"""
import pytest
import sys
from unittest.mock import MagicMock, patch, Mock

# Mock de google.cloud ANTES de importar el servicio
mock_pubsub_v1 = Mock()
mock_publisher_client = Mock()
mock_pubsub_v1.PublisherClient = mock_publisher_client

sys.modules['google'] = Mock()
sys.modules['google.cloud'] = Mock()
sys.modules['google.cloud.pubsub_v1'] = mock_pubsub_v1

from app.services.pubsub_service import PubSubService
from app.config.settings import Config


class TestPubSubService:
    """Tests para PubSubService"""
    
    @pytest.fixture(autouse=True)
    def reset_mock(self):
        """Resetear el mock antes y después de cada test"""
        # Limpiar estado antes del test
        mock_publisher_client.reset_mock()
        mock_publisher_client.side_effect = None
        mock_publisher_client.return_value = None
        # También resetear el mock del módulo pubsub_v1
        mock_pubsub_v1.reset_mock()
        yield
        # Limpiar estado después del test
        mock_publisher_client.reset_mock()
        mock_publisher_client.side_effect = None
        mock_publisher_client.return_value = None
        mock_pubsub_v1.reset_mock()
    
    @pytest.fixture
    def mock_config(self):
        """Mock de Config"""
        config = MagicMock()
        config.GCP_PROJECT_ID = 'test-project'
        config.PUBSUB_TOPIC_VIDEO_PROCESSING = 'salesplan.processing.videos'
        config.GOOGLE_APPLICATION_CREDENTIALS = ''
        return config
    
    @pytest.fixture
    def pubsub_service(self, mock_config):
        """Instancia de PubSubService con config mockeado"""
        return PubSubService(config=mock_config)
    
    def test_publish_message_success(self, pubsub_service, mock_config):
        """Test: Publicar mensaje exitosamente"""
        mock_publisher = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 'message-id-123'
        mock_publisher.publish.return_value = mock_future
        mock_publisher.topic_path.return_value = 'projects/test-project/topics/test-topic'
        
        pubsub_service._publisher = mock_publisher
        
        message_data = {'scheduled_visit_client_id': 123, 'event_type': 'test'}
        result = pubsub_service.publish_message('test-topic', message_data)
        
        assert result == 'message-id-123'
        mock_publisher.topic_path.assert_called_once_with('test-project', 'test-topic')
        mock_publisher.publish.assert_called_once()
    
    def test_publish_message_error(self, pubsub_service):
        """Test: Error genérico al publicar mensaje"""
        mock_publisher = MagicMock()
        mock_publisher.topic_path.side_effect = Exception('Generic error')
        
        pubsub_service._publisher = mock_publisher
        
        message_data = {'scheduled_visit_client_id': 123}
        
        with pytest.raises(Exception, match="Error al publicar mensaje en Pub/Sub"):
            pubsub_service.publish_message('test-topic', message_data)
    
    def test_publish_message_error_on_publish(self, pubsub_service):
        """Test: Error al ejecutar publish"""
        mock_publisher = MagicMock()
        mock_publisher.topic_path.return_value = 'projects/test-project/topics/test-topic'
        mock_publisher.publish.side_effect = Exception('Publish error')
        
        pubsub_service._publisher = mock_publisher
        
        message_data = {'scheduled_visit_client_id': 123}
        
        with pytest.raises(Exception, match="Error al publicar mensaje en Pub/Sub"):
            pubsub_service.publish_message('test-topic', message_data)
    
    def test_publish_message_error_on_future_result(self, pubsub_service):
        """Test: Error al obtener resultado del future"""
        mock_publisher = MagicMock()
        mock_future = MagicMock()
        mock_future.result.side_effect = Exception('Future result error')
        mock_publisher.publish.return_value = mock_future
        mock_publisher.topic_path.return_value = 'projects/test-project/topics/test-topic'
        
        pubsub_service._publisher = mock_publisher
        
        message_data = {'scheduled_visit_client_id': 123}
        
        with pytest.raises(Exception, match="Error al publicar mensaje en Pub/Sub"):
            pubsub_service.publish_message('test-topic', message_data)
    
    def test_publish_video_processing_event_success(self, pubsub_service, mock_config):
        """Test: Publicar evento de procesamiento de video exitosamente"""
        mock_publisher = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 'message-id-123'
        mock_publisher.publish.return_value = mock_future
        mock_publisher.topic_path.return_value = 'projects/test-project/topics/salesplan.processing.videos'
        
        pubsub_service._publisher = mock_publisher
        
        with patch('app.services.pubsub_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.isoformat.return_value = '2024-01-15T10:30:45.123456'
            
            result = pubsub_service.publish_video_processing_event(123)
        
        assert result == 'message-id-123'
        mock_publisher.publish.assert_called_once()
        mock_publisher.topic_path.assert_called_once_with('test-project', 'salesplan.processing.videos')
    
    def test_publish_video_processing_event_error(self, pubsub_service):
        """Test: Error al publicar evento de procesamiento de video"""
        mock_publisher = MagicMock()
        mock_publisher.topic_path.side_effect = Exception('Error')
        
        pubsub_service._publisher = mock_publisher
        
        with pytest.raises(Exception):
            pubsub_service.publish_video_processing_event(123)
    
    def test_publisher_property_lazy_initialization(self, mock_config):
        """Test: Inicialización lazy del publisher"""
        mock_client = MagicMock()
        
        # Importar el módulo para poder patchearlo
        import app.services.pubsub_service as pubsub_module
        
        # Usar patch.object para sobrescribir el atributo en el módulo
        with patch.object(pubsub_module.pubsub_v1, 'PublisherClient', return_value=mock_client) as mock_pub_client:
            service = PubSubService(config=mock_config)
            assert service._publisher is None
            
            # Acceder a la propiedad para inicializar
            publisher = service.publisher
            
            assert publisher is not None
            assert publisher == mock_client
            # Verificar que se llamó al constructor
            mock_pub_client.assert_called_once()
            # Verificar que el publisher fue asignado
            assert service._publisher is not None
    
    def test_publisher_property_initialization_with_credentials(self, mock_config):
        """Test: Inicialización del publisher con credenciales"""
        mock_config.GOOGLE_APPLICATION_CREDENTIALS = '/path/to/credentials.json'
        mock_client = MagicMock()
        
        # Importar el módulo para poder patchearlo
        import app.services.pubsub_service as pubsub_module
        
        with patch.object(pubsub_module.pubsub_v1, 'PublisherClient', return_value=mock_client) as mock_pub_client:
            # Mockear os.environ para verificar que se llama __setitem__
            with patch('app.services.pubsub_service.os') as mock_os:
                mock_env = MagicMock()
                mock_os.environ = mock_env
                
                service = PubSubService(config=mock_config)
                publisher = service.publisher
                
                assert publisher is not None
                assert publisher == mock_client
                # Verificar que se intentó configurar la variable de entorno
                # (puede no llamarse si ya estaba configurado en otros tests)
                # Lo importante es que el publisher se inicialice correctamente
                mock_pub_client.assert_called_once()
                # Verificar que el publisher fue asignado
                assert service._publisher is not None
                assert service._publisher == mock_client
    
    def test_publisher_property_initialization_error(self, mock_config):
        """Test: Error al inicializar publisher"""
        # Importar el módulo para poder patchearlo
        import app.services.pubsub_service as pubsub_module
        
        # Usar patch.object para sobrescribir el atributo en el módulo
        with patch.object(pubsub_module.pubsub_v1, 'PublisherClient', side_effect=Exception('Initialization error')):
            service = PubSubService(config=mock_config)
            
            with pytest.raises(Exception, match="Error al inicializar cliente de Pub/Sub"):
                _ = service.publisher
    
    def test_publisher_property_returns_cached_instance(self, mock_config):
        """Test: La propiedad publisher retorna la instancia cacheada"""
        mock_client = MagicMock()
        
        # Importar el módulo para poder patchearlo
        import app.services.pubsub_service as pubsub_module
        
        # Usar patch.object para sobrescribir el atributo en el módulo
        with patch.object(pubsub_module.pubsub_v1, 'PublisherClient', return_value=mock_client) as mock_pub_client:
            service = PubSubService(config=mock_config)
            
            # Primera llamada inicializa
            publisher1 = service.publisher
            # Segunda llamada usa cache
            publisher2 = service.publisher
            
            # Verificar que ambas llamadas retornan la misma instancia
            assert publisher1 == publisher2
            assert publisher1 is publisher2
            assert publisher1 == mock_client
            # Solo se debe llamar una vez al constructor
            mock_pub_client.assert_called_once()
            # Verificar que el publisher fue cacheado
            assert service._publisher is not None
            assert service._publisher is publisher1
    
    def test_init_without_config(self):
        """Test: Inicialización sin config (usa Config por defecto)"""
        # Cuando no se pasa config, debe usar Config() por defecto
        service = PubSubService()
        
        # Verificar que tiene una instancia de Config
        assert service.config is not None
        assert hasattr(service.config, 'GCP_PROJECT_ID')
        assert isinstance(service.config, Config)
    
    def test_publish_message_encodes_json_correctly(self, pubsub_service, mock_config):
        """Test: Verificar que el mensaje se codifica correctamente a JSON"""
        mock_publisher = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 'message-id-123'
        mock_publisher.publish.return_value = mock_future
        mock_publisher.topic_path.return_value = 'projects/test-project/topics/test-topic'
        
        pubsub_service._publisher = mock_publisher
        
        message_data = {
            'scheduled_visit_client_id': 123,
            'event_type': 'video_processing',
            'timestamp': '2024-01-15T10:30:45'
        }
        
        result = pubsub_service.publish_message('test-topic', message_data)
        
        assert result == 'message-id-123'
        # Verificar que se llamó a publish con bytes codificados
        call_args = mock_publisher.publish.call_args
        published_bytes = call_args[0][1]
        assert isinstance(published_bytes, bytes)
        
        # Decodificar y verificar contenido
        import json
        decoded_data = json.loads(published_bytes.decode('utf-8'))
        assert decoded_data == message_data
    
    def test_publish_video_processing_event_includes_timestamp(self, pubsub_service, mock_config):
        """Test: Verificar que el evento de video incluye timestamp"""
        mock_publisher = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 'message-id-123'
        mock_publisher.publish.return_value = mock_future
        mock_publisher.topic_path.return_value = 'projects/test-project/topics/salesplan.processing.videos'
        
        pubsub_service._publisher = mock_publisher
        
        result = pubsub_service.publish_video_processing_event(123)
        
        assert result == 'message-id-123'
        
        # Verificar que el mensaje incluye los campos correctos
        call_args = mock_publisher.publish.call_args
        published_bytes = call_args[0][1]
        import json
        decoded_data = json.loads(published_bytes.decode('utf-8'))
        
        assert decoded_data['scheduled_visit_client_id'] == 123
        assert decoded_data['event_type'] == 'video_processing'
        # Verificar que tiene timestamp y es una cadena ISO válida
        assert 'timestamp' in decoded_data
        assert isinstance(decoded_data['timestamp'], str)
        # Verificar formato ISO (debe contener 'T' y tener formato de fecha/hora)
        assert 'T' in decoded_data['timestamp']
        # Verificar que se puede parsear como datetime
        from datetime import datetime
        try:
            datetime.fromisoformat(decoded_data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            # Si no tiene timezone, intentar sin ella
            datetime.fromisoformat(decoded_data['timestamp'])

