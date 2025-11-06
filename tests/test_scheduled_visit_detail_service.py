"""
Tests para el servicio ScheduledVisitDetailService
"""
import pytest
from unittest.mock import Mock, patch
from datetime import date
from app.services.scheduled_visit_detail_service import ScheduledVisitDetailService
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


class TestScheduledVisitDetailService:
    """Tests para ScheduledVisitDetailService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """Servicio con repositorio mockeado"""
        return ScheduledVisitDetailService(mock_repository)
    
    def test_get_visit_detail_success(self, service, mock_repository):
        """Test obtener detalle de visita exitosamente"""
        from datetime import datetime
        
        # Crear visita mock
        mock_visit = Mock()
        mock_visit.id = 'visit1'
        mock_visit.seller_id = 'seller1'
        mock_visit.date = date(2025, 12, 1)
        mock_visit.created_at = datetime(2025, 11, 1, 10, 0, 0)
        mock_visit.updated_at = datetime(2025, 11, 1, 10, 0, 0)
        
        # Crear clientes mock
        client1 = Mock()
        client1.client_id = 'client1'
        client2 = Mock()
        client2.client_id = 'client2'
        mock_visit.clients = [client1, client2]
        
        # Configurar mocks
        with patch.object(service, '_validate_seller_exists', return_value=True):
            with patch.object(service, '_get_client_detail', side_effect=[
                {'id': 'client1', 'name': 'Cliente 1'},
                {'id': 'client2', 'name': 'Cliente 2'}
            ]):
                mock_repository.get_by_id_and_seller.return_value = mock_visit
                
                result = service.get_visit_detail('visit1', 'seller1')
                
                assert result['id'] == 'visit1'
                assert result['seller_id'] == 'seller1'
                assert result['date'] == '01-12-2025'
                assert len(result['clients']) == 2
    
    def test_get_visit_detail_seller_not_found(self, service, mock_repository):
        """Test obtener detalle con vendedor que no existe"""
        with patch.object(service, '_validate_seller_exists', return_value=False):
            with pytest.raises(SalesPlanValidationError, match="El vendedor con ID seller1 no existe"):
                service.get_visit_detail('visit1', 'seller1')
    
    def test_get_visit_detail_visit_not_found(self, service, mock_repository):
        """Test obtener detalle de visita que no existe"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            mock_repository.get_by_id_and_seller.return_value = None
            
            with pytest.raises(SalesPlanValidationError, match="No se encontró la visita"):
                service.get_visit_detail('visit1', 'seller1')
    
    def test_get_visit_detail_repository_error(self, service, mock_repository):
        """Test error del repositorio al obtener detalle"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            mock_repository.get_by_id_and_seller.side_effect = Exception("Database error")
            
            with pytest.raises(SalesPlanBusinessLogicError, match="Error al obtener detalle de visita"):
                service.get_visit_detail('visit1', 'seller1')
    
    @patch('requests.get')
    def test_validate_seller_exists_success(self, mock_get, service):
        """Test validar que vendedor existe"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = service._validate_seller_exists('seller1')
        
        assert result is True
    
    @patch('requests.get')
    def test_validate_seller_exists_not_found(self, mock_get, service):
        """Test validar que vendedor no existe"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = service._validate_seller_exists('seller1')
        
        assert result is False
    
    @patch('requests.get')
    def test_validate_seller_exists_request_exception(self, mock_get, service):
        """Test validar vendedor con excepción de requests"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException()
        
        result = service._validate_seller_exists('seller1')
        
        assert result is False
    
    @patch('requests.get')
    def test_get_client_detail_success_with_data_wrapper(self, mock_get, service):
        """Test obtener detalle de cliente con respuesta envuelta en 'data'"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': 'Usuario obtenido exitosamente',
            'data': {
                'id': 'client1',
                'name': 'Hospital General',
                'email': 'test@example.com'
            }
        }
        mock_get.return_value = mock_response
        
        result = service._get_client_detail('client1')
        
        assert result is not None
        assert result['id'] == 'client1'
        assert result['name'] == 'Hospital General'
    
    @patch('requests.get')
    def test_get_client_detail_success_without_wrapper(self, mock_get, service):
        """Test obtener detalle de cliente con respuesta directa"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'client1',
            'name': 'Hospital General',
            'email': 'test@example.com'
        }
        mock_get.return_value = mock_response
        
        result = service._get_client_detail('client1')
        
        assert result is not None
        assert result['id'] == 'client1'
        assert result['name'] == 'Hospital General'
    
    @patch('requests.get')
    def test_get_client_detail_not_found(self, mock_get, service):
        """Test obtener detalle de cliente que no existe"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = service._get_client_detail('client1')
        
        assert result is None
    
    @patch('requests.get')
    def test_get_client_detail_request_exception(self, mock_get, service):
        """Test obtener detalle de cliente con excepción de requests"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException()
        
        result = service._get_client_detail('client1')
        
        assert result is None
    
    def test_get_visit_detail_with_no_client_details(self, service, mock_repository):
        """Test obtener detalle de visita cuando los clientes no retornan datos"""
        from datetime import datetime
        
        # Crear visita mock
        mock_visit = Mock()
        mock_visit.id = 'visit1'
        mock_visit.seller_id = 'seller1'
        mock_visit.date = date(2025, 12, 1)
        mock_visit.created_at = datetime(2025, 11, 1, 10, 0, 0)
        mock_visit.updated_at = datetime(2025, 11, 1, 10, 0, 0)
        
        # Crear cliente mock
        client1 = Mock()
        client1.client_id = 'client1'
        mock_visit.clients = [client1]
        
        # Configurar mocks para que _get_client_detail retorne None
        with patch.object(service, '_validate_seller_exists', return_value=True):
            with patch.object(service, '_get_client_detail', return_value=None):
                mock_repository.get_by_id_and_seller.return_value = mock_visit
                
                result = service.get_visit_detail('visit1', 'seller1')
                
                assert result['id'] == 'visit1'
                assert len(result['clients']) == 0  # No se agregaron clientes porque retornaron None
    
    def test_init_service(self, mock_repository):
        """Test inicialización del servicio"""
        service = ScheduledVisitDetailService(mock_repository)
        
        assert service.scheduled_visit_repository == mock_repository
        assert service.auth_service_url is not None

