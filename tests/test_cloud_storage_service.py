"""
Pruebas unitarias para CloudStorageService
Estas pruebas se enfocan en los métodos públicos principales
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Mock de google.cloud ANTES de importar el servicio
mock_storage_client = Mock()
mock_storage = Mock()
mock_storage.Client = mock_storage_client
mock_exceptions = Mock()

class GoogleCloudError(Exception):
    pass

mock_exceptions.GoogleCloudError = GoogleCloudError

sys.modules['google'] = Mock()
sys.modules['google.cloud'] = Mock()
sys.modules['google.cloud.storage'] = mock_storage
sys.modules['google.cloud.exceptions'] = mock_exceptions
sys.modules['google.auth'] = Mock()
sys.modules['google.auth.impersonated_credentials'] = Mock()

# Mock de PIL.Image ANTES de importar el servicio
mock_pil = Mock()
mock_image = Mock()
mock_pil.Image = mock_image
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = mock_image

from app.services.cloud_storage_service import CloudStorageService


@pytest.fixture
def mock_config():
    """Configuración mock"""
    config = Mock()
    config.BUCKET_NAME = 'test-bucket'
    config.BUCKET_FOLDER = 'test-folder'
    config.GCP_PROJECT_ID = 'test-project'
    config.GOOGLE_APPLICATION_CREDENTIALS = '/path/to/credentials.json'
    config.MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    config.SIGNING_SERVICE_ACCOUNT_EMAIL = 'test@test.com'
    return config


@pytest.fixture
def service(mock_config):
    """Servicio de Cloud Storage con config mockeada"""
    return CloudStorageService(config=mock_config)


class TestCloudStorageService:
    """Pruebas para CloudStorageService"""
    
    def test_init_with_config(self, service, mock_config):
        """Prueba inicialización con configuración"""
        assert service.config == mock_config
        assert service._client is None
        assert service._bucket is None
    
    def test_client_property_initializes_storage_client(self, mock_config):
        """Prueba que la propiedad client inicializa el cliente de storage"""
        service = CloudStorageService(config=mock_config)
        
        # Acceder a la propiedad client debe inicializarlo
        client = service.client
        assert client is not None
        assert service._client is not None
    
    def test_bucket_property_initializes_bucket(self, mock_config):
        """Prueba que la propiedad bucket inicializa el bucket"""
        service = CloudStorageService(config=mock_config)
        
        # Acceder a la propiedad bucket debe inicializarlo
        bucket = service.bucket
        assert bucket is not None
        assert service._bucket is not None
    
    def test_validate_image_file_no_filename(self, service):
        """Prueba validar archivo sin nombre"""
        mock_file = Mock()
        mock_file.filename = ''
        
        is_valid, error = service.validate_image_file(mock_file)
        
        assert is_valid is False
        assert "No se proporcionó archivo" in error
    
    def test_validate_image_file_no_extension(self, service):
        """Prueba validar archivo sin extensión"""
        mock_file = Mock()
        mock_file.filename = 'test'
        
        is_valid, error = service.validate_image_file(mock_file)
        
        assert is_valid is False
        assert "no tiene extensión" in error
    
    def test_validate_image_file_invalid_extension(self, service):
        """Prueba validar archivo con extensión inválida"""
        mock_file = Mock()
        mock_file.filename = 'test.txt'
        
        is_valid, error = service.validate_image_file(mock_file)
        
        assert is_valid is False
        assert "Extensión no permitida" in error
    
    def test_validate_image_file_too_large(self, service):
        """Prueba validar archivo muy grande"""
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=11 * 1024 * 1024)
        
        is_valid, error = service.validate_image_file(mock_file)
        
        assert is_valid is False
        assert "El archivo es demasiado grande" in error
    
    def test_validate_image_file_invalid_image(self, service):
        """Prueba validar archivo de imagen inválido"""
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024)
        
        with patch('app.services.cloud_storage_service.Image') as mock_image:
            mock_image.open.side_effect = Exception("Invalid image")
            
            is_valid, error = service.validate_image_file(mock_file)
            
            assert is_valid is False
            assert "El archivo no es una imagen válida" in error
    
    def test_delete_image_success_when_exists(self, service):
        """Prueba eliminar imagen cuando existe"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        service._bucket = mock_bucket
        
        success, message = service.delete_image('test.jpg')
        
        assert success is True
        assert message == "Imagen eliminada exitosamente"
        mock_blob.delete.assert_called_once()
    
    def test_delete_image_when_not_exists(self, service):
        """Prueba eliminar imagen cuando no existe"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = False
        service._bucket = mock_bucket
        
        success, message = service.delete_image('test.jpg')
        
        assert success is False
        assert message == "La imagen no existe"
        mock_blob.delete.assert_not_called()
    
    def test_delete_image_gcs_error(self, service):
        """Prueba eliminar imagen con error de GCS"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.delete.side_effect = GoogleCloudError("Delete error")
        service._bucket = mock_bucket
        
        success, message = service.delete_image('test.jpg')
        
        assert success is False
        assert "Error de Google Cloud Storage" in message
    
    def test_delete_image_generic_error(self, service):
        """Prueba eliminar imagen con error genérico"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        mock_blob.delete.side_effect = Exception("Generic error")
        service._bucket = mock_bucket
        
        success, message = service.delete_image('test.jpg')
        
        assert success is False
        assert "Error al eliminar imagen" in message
    
    def test_upload_file_too_large(self, service):
        """Prueba subir archivo que excede el tamaño máximo"""
        mock_file = Mock()
        mock_file.filename = 'large.pdf'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=11 * 1024 * 1024)
        
        success, message, url = service.upload_file(mock_file, 'large.pdf')
        
        assert success is False
        assert "excede el tamaño máximo" in message
        assert url is None
    
    def test_upload_file_no_filename(self, service):
        """Prueba subir archivo sin nombre"""
        mock_file = Mock()
        mock_file.filename = ''
        
        success, message, url = service.upload_file(mock_file, 'test.pdf')
        
        assert success is False
        assert "No se proporcionó archivo" in message
        assert url is None
    
    def test_upload_file_no_file_object(self, service):
        """Prueba subir sin proporcionar objeto de archivo"""
        success, message, url = service.upload_file(None, 'test.pdf')
        
        assert success is False
        assert "No se proporcionó archivo" in message
        assert url is None
    
    def test_get_file_url_calls_get_image_url(self, service):
        """Prueba que get_file_url llama a get_image_url"""
        with patch.object(service, 'get_image_url', return_value='test_url') as mock_get_image:
            url = service.get_file_url('test.pdf', 48)
            
            assert url == 'test_url'
            mock_get_image.assert_called_once_with('test.pdf', 48)
    
    def test_upload_file_success_pdf(self, service):
        """Prueba subir archivo PDF exitosamente"""
        # Setup mocks
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        # Set mock bucket directamente en el atributo privado
        service._bucket = mock_bucket
        
        mock_file = Mock()
        mock_file.filename = 'test.pdf'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024 * 1024)
        
        # Mockear get_file_url
        with patch.object(service, 'get_file_url', return_value='https://storage.googleapis.com/bucket/test.pdf'):
            success, message, url = service.upload_file(mock_file, 'test.pdf')
            
            assert success is True
            assert message == "Archivo subido exitosamente"
            assert url == 'https://storage.googleapis.com/bucket/test.pdf'
            
            # Verificar que se llamó upload_from_file
            mock_blob.upload_from_file.assert_called_once()
            # Verificar que el content type es correcto
            call_kwargs = mock_blob.upload_from_file.call_args[1]
            assert call_kwargs['content_type'] == 'application/pdf'
    
    def test_upload_file_success_image(self, service):
        """Prueba subir archivo de imagen exitosamente"""
        # Setup mocks
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        # Set mock bucket directamente en el atributo privado
        service._bucket = mock_bucket
        
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024 * 1024)
        
        # Mockear get_file_url
        with patch.object(service, 'get_file_url', return_value='https://storage.googleapis.com/bucket/test.jpg'):
            success, message, url = service.upload_file(mock_file, 'test.jpg')
            
            assert success is True
            assert message == "Archivo subido exitosamente"
            assert url == 'https://storage.googleapis.com/bucket/test.jpg'
            
            # Verificar que el content type es correcto
            call_kwargs = mock_blob.upload_from_file.call_args[1]
            assert call_kwargs['content_type'] == 'image/jpeg'
    
    def test_upload_file_gcs_error(self, service):
        """Prueba subir archivo con error de GCS"""
        # Setup mocks
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        # Simular error al subir
        mock_blob.upload_from_file.side_effect = GoogleCloudError("Upload failed")
        
        # Set mock bucket directamente en el atributo privado
        service._bucket = mock_bucket
        
        mock_file = Mock()
        mock_file.filename = 'test.pdf'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024)
        
        success, message, url = service.upload_file(mock_file, 'test.pdf')
        
        assert success is False
        assert "Error de Google Cloud Storage" in message
        assert url is None
    
    def test_upload_file_generic_error(self, service):
        """Prueba subir archivo con error genérico"""
        # Setup mocks
        mock_bucket = Mock()
        mock_bucket.blob.side_effect = Exception("Generic error")
        
        # Set mock bucket directamente en el atributo privado
        service._bucket = mock_bucket
        
        mock_file = Mock()
        mock_file.filename = 'test.pdf'
        mock_file.seek = Mock()
        mock_file.tell = Mock(return_value=1024)
        
        success, message, url = service.upload_file(mock_file, 'test.pdf')
        
        assert success is False
        assert "Error al subir archivo" in message
        assert url is None
    
    def test_get_image_url_file_not_exists_returns_empty(self, service):
        """Prueba que get_image_url retorna vacío cuando el archivo no existe"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.return_value = False
        service._bucket = mock_bucket
        
        url = service.get_image_url('nonexistent.jpg')
        
        assert url == ""
        mock_blob.exists.assert_called_once()
    
    def test_get_image_url_falls_back_on_error(self, service):
        """Prueba que get_image_url retorna URL directa cuando falla la firma"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        mock_blob.exists.side_effect = Exception("Connection error")
        service._bucket = mock_bucket
        
        url = service.get_image_url('test.jpg')
        
        # Debe retornar la URL directa como fallback
        assert 'https://storage.googleapis.com' in url
        assert service.config.BUCKET_NAME in url
        assert 'test.jpg' in url
    
    def test_upload_file_with_different_extensions(self, service):
        """Prueba subir archivos con diferentes extensiones"""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        service._bucket = mock_bucket
        
        test_cases = [
            ('test.pdf', 'application/pdf'),
            ('test.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            ('test.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('test.txt', 'text/plain'),
        ]
        
        for filename, expected_content_type in test_cases:
            mock_file = Mock()
            mock_file.filename = filename
            mock_file.seek = Mock()
            mock_file.tell = Mock(return_value=1024)
            
            with patch.object(service, 'get_file_url', return_value=f'https://storage.googleapis.com/bucket/{filename}'):
                success, message, url = service.upload_file(mock_file, filename)
                
                assert success is True
                # Verificar que se llamó con el content_type correcto
                call_kwargs = mock_blob.upload_from_file.call_args[1]
                assert call_kwargs['content_type'] == expected_content_type
