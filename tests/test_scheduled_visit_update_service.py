"""
Tests para el servicio ScheduledVisitUpdateService
"""
import pytest
import sys
from unittest.mock import Mock, patch
from datetime import date
from io import BytesIO

# Mock de CloudStorageService para evitar conflictos de importación con google.cloud
sys.modules['app.services.cloud_storage_service'] = Mock()

from app.services.scheduled_visit_update_service import ScheduledVisitUpdateService
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


class TestScheduledVisitUpdateService:
    """Tests para ScheduledVisitUpdateService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio"""
        return Mock()
    
    @pytest.fixture
    def mock_cloud_storage(self):
        """Mock del servicio de Cloud Storage"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository, mock_cloud_storage):
        """Servicio con repositorio y cloud storage mockeados"""
        return ScheduledVisitUpdateService(mock_repository, mock_cloud_storage)
    
    def test_update_client_visit_success(self, service, mock_repository):
        """Test actualizar cliente de visita exitosamente"""
        # Mock de la visita
        mock_visit = Mock()
        mock_visit.id = 'visit1'
        mock_visit.seller_id = 'seller1'
        
        # Mock del cliente en la visita
        mock_client_visit = Mock()
        mock_client_visit.visit_id = 'visit1'
        mock_client_visit.client_id = 'client1'
        mock_client_visit.status = 'SCHEDULED'
        
        mock_repository.get_by_id_and_seller.return_value = mock_visit
        mock_repository.get_client_visit.return_value = mock_client_visit
        mock_repository.update_client_visit.return_value = True
        
        result = service.update_client_visit(
            seller_id='seller1',
            visit_id='visit1',
            client_id='client1',
            find='Hallazgos importantes'
        )
        
        assert result['visit_id'] == 'visit1'
        assert result['client_id'] == 'client1'
        assert result['status'] == 'COMPLETED'
        assert result['find'] == 'Hallazgos importantes'
        
        # Verificar que se llamó a update_client_visit con los datos correctos
        mock_repository.update_client_visit.assert_called_once()
        call_args = mock_repository.update_client_visit.call_args
        assert call_args[0][0] == 'visit1'
        assert call_args[0][1] == 'client1'
        assert call_args[0][2]['status'] == 'COMPLETED'
        assert call_args[0][2]['find'] == 'Hallazgos importantes'
    
    def test_update_client_visit_not_found(self, service, mock_repository):
        """Test actualizar visita que no existe"""
        mock_repository.get_by_id_and_seller.return_value = None
        
        with pytest.raises(SalesPlanValidationError, match="No se encontró la visita"):
            service.update_client_visit(
                seller_id='seller1',
                visit_id='visit1',
                client_id='client1',
                find='Hallazgos'
            )
    
    def test_update_client_not_in_visit(self, service, mock_repository):
        """Test actualizar cliente que no existe en la visita"""
        mock_visit = Mock()
        mock_visit.id = 'visit1'
        
        mock_repository.get_by_id_and_seller.return_value = mock_visit
        mock_repository.get_client_visit.return_value = None
        
        with pytest.raises(SalesPlanValidationError, match="No se encontró el cliente"):
            service.update_client_visit(
                seller_id='seller1',
                visit_id='visit1',
                client_id='client1',
                find='Hallazgos'
            )
    
    def test_update_client_visit_update_failed(self, service, mock_repository):
        """Test cuando falla la actualización"""
        mock_visit = Mock()
        mock_client_visit = Mock()
        
        mock_repository.get_by_id_and_seller.return_value = mock_visit
        mock_repository.get_client_visit.return_value = mock_client_visit
        mock_repository.update_client_visit.return_value = False
        
        with pytest.raises(SalesPlanBusinessLogicError, match="No se pudo actualizar"):
            service.update_client_visit(
                seller_id='seller1',
                visit_id='visit1',
                client_id='client1',
                find='Hallazgos'
            )
    
    def test_update_client_visit_repository_error(self, service, mock_repository):
        """Test error del repositorio al actualizar"""
        mock_visit = Mock()
        mock_client_visit = Mock()
        
        mock_repository.get_by_id_and_seller.return_value = mock_visit
        mock_repository.get_client_visit.return_value = mock_client_visit
        mock_repository.update_client_visit.side_effect = Exception("Database error")
        
        with pytest.raises(SalesPlanBusinessLogicError, match="Error al actualizar cliente de la visita"):
            service.update_client_visit(
                seller_id='seller1',
                visit_id='visit1',
                client_id='client1',
                find='Hallazgos'
            )
    
    def test_init_service(self, mock_repository, mock_cloud_storage):
        """Test inicialización del servicio"""
        service = ScheduledVisitUpdateService(mock_repository, mock_cloud_storage)
        
        assert service.scheduled_visit_repository == mock_repository
        assert service.cloud_storage_service == mock_cloud_storage
    
    def test_update_client_visit_with_file_success(self, service, mock_repository, mock_cloud_storage):
        """Test actualizar cliente de visita con archivo exitosamente"""
        # Mock de la visita
        mock_visit = Mock()
        mock_visit.id = 'visit1'
        mock_visit.seller_id = 'seller1'
        
        # Mock del cliente en la visita
        mock_client_visit = Mock()
        mock_client_visit.visit_id = 'visit1'
        mock_client_visit.client_id = 'client1'
        mock_client_visit.status = 'SCHEDULED'
        
        # Mock del archivo
        mock_file = Mock()
        mock_file.filename = 'test.pdf'
        mock_file.seek = Mock()
        
        mock_repository.get_by_id_and_seller.return_value = mock_visit
        mock_repository.get_client_visit.return_value = mock_client_visit
        mock_repository.update_client_visit.return_value = True
        mock_cloud_storage.upload_file.return_value = (True, "Archivo subido", "https://storage.googleapis.com/bucket/file.pdf")
        
        result = service.update_client_visit(
            seller_id='seller1',
            visit_id='visit1',
            client_id='client1',
            find='Hallazgos importantes',
            file=mock_file
        )
        
        assert result['visit_id'] == 'visit1'
        assert result['client_id'] == 'client1'
        assert result['status'] == 'COMPLETED'
        assert result['find'] == 'Hallazgos importantes'
        assert result['filename'] is not None
        # Verificar que el filename tiene el formato correcto: nombre_base-uuid.extension
        assert result['filename'].startswith('test-')
        assert result['filename'].endswith('.pdf')
        assert result['filename_url'] == "https://storage.googleapis.com/bucket/file.pdf"
        
        # Verificar que se llamó a upload_file con el nombre correcto
        mock_cloud_storage.upload_file.assert_called_once()
        call_args = mock_cloud_storage.upload_file.call_args
        uploaded_filename = call_args[0][1]
        # El filename debe tener formato: test-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.pdf (UUID completo de 32 caracteres)
        assert uploaded_filename.startswith('test-')
        assert uploaded_filename.endswith('.pdf')
        assert len(uploaded_filename.split('-')[1].split('.')[0]) == 32  # UUID completo de 32 caracteres hexadecimales
    
    def test_update_client_visit_file_upload_fails(self, service, mock_repository, mock_cloud_storage):
        """Test cuando falla la subida del archivo"""
        # Mock de la visita
        mock_visit = Mock()
        mock_visit.id = 'visit1'
        
        # Mock del cliente en la visita
        mock_client_visit = Mock()
        mock_client_visit.visit_id = 'visit1'
        mock_client_visit.client_id = 'client1'
        
        # Mock del archivo
        mock_file = Mock()
        mock_file.filename = 'test.pdf'
        
        mock_repository.get_by_id_and_seller.return_value = mock_visit
        mock_repository.get_client_visit.return_value = mock_client_visit
        mock_cloud_storage.upload_file.return_value = (False, "Error al subir archivo", None)
        
        with pytest.raises(SalesPlanBusinessLogicError, match="Error al subir archivo"):
            service.update_client_visit(
                seller_id='seller1',
                visit_id='visit1',
                client_id='client1',
                find='Hallazgos',
                file=mock_file
            )

