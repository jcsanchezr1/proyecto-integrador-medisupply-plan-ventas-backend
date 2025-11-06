"""
Tests para el servicio ScheduledVisitService
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date
from app.services.scheduled_visit_service import ScheduledVisitService
from app.repositories.scheduled_visit_repository import ScheduledVisitRepository
from app.models.scheduled_visit import ScheduledVisit, ScheduledVisitClient
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


class TestScheduledVisitService:
    """Tests para el servicio ScheduledVisitService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio"""
        return Mock(spec=ScheduledVisitRepository)
    
    @pytest.fixture
    def service(self, mock_repository):
        """Servicio con repositorio mockeado"""
        return ScheduledVisitService(mock_repository)
    
    @pytest.fixture
    def sample_visit_data(self):
        """Datos de muestra para crear visita"""
        return {
            'seller_id': 'c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'date': '01-12-2025',
            'clients': [
                {'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'},
                {'client_id': 'b527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}
            ]
        }
    
    def test_create_scheduled_visit_success(self, service, sample_visit_data, mock_repository):
        """Test crear visita programada exitosamente"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            with patch.object(service, '_validate_client_exists', return_value=True):
                mock_visit = Mock(spec=ScheduledVisit)
                mock_visit.id = 'visit1'
                mock_visit.to_dict.return_value = {'id': 'visit1'}
                mock_repository.create.return_value = mock_visit
                
                result = service.create_scheduled_visit(sample_visit_data)
                
                assert result == mock_visit
                mock_repository.create.assert_called_once()
    
    def test_create_scheduled_visit_seller_not_found(self, service, sample_visit_data):
        """Test crear visita con vendedor inexistente"""
        with patch.object(service, '_validate_seller_exists', return_value=False):
            with pytest.raises(SalesPlanValidationError, match="no existe"):
                service.create_scheduled_visit(sample_visit_data)
    
    def test_create_scheduled_visit_invalid_date_format(self, service, sample_visit_data):
        """Test crear visita con formato de fecha inválido"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            sample_visit_data['date'] = '2025-12-01'  # Formato incorrecto
            
            with pytest.raises(SalesPlanValidationError, match="formato de fecha"):
                service.create_scheduled_visit(sample_visit_data)
    
    def test_create_scheduled_visit_empty_clients(self, service, sample_visit_data):
        """Test crear visita sin clientes"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            sample_visit_data['clients'] = []
            
            with pytest.raises(SalesPlanValidationError, match="al menos un cliente"):
                service.create_scheduled_visit(sample_visit_data)
    
    def test_create_scheduled_visit_missing_clients(self, service, sample_visit_data):
        """Test crear visita sin campo clients"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            del sample_visit_data['clients']
            
            with pytest.raises(SalesPlanValidationError, match="al menos un cliente"):
                service.create_scheduled_visit(sample_visit_data)
    
    def test_create_scheduled_visit_client_not_found(self, service, sample_visit_data):
        """Test crear visita con cliente inexistente"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            with patch.object(service, '_validate_client_exists', return_value=False):
                with pytest.raises(SalesPlanValidationError, match="El cliente con ID"):
                    service.create_scheduled_visit(sample_visit_data)
    
    def test_create_scheduled_visit_missing_client_id(self, service, sample_visit_data):
        """Test crear visita con cliente sin ID"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            sample_visit_data['clients'] = [{'client_id': None}]
            
            with pytest.raises(SalesPlanValidationError, match="client_id es obligatorio"):
                service.create_scheduled_visit(sample_visit_data)
    
    def test_create_scheduled_visit_duplicate_date_seller(self, service, sample_visit_data, mock_repository):
        """Test crear visita con fecha y vendedor duplicados"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            with patch.object(service, '_validate_client_exists', return_value=True):
                mock_repository.create.side_effect = ValueError("Ya existe una visita programada para este vendedor en la fecha 01-12-2025")
                
                with pytest.raises(SalesPlanValidationError, match="Ya existe una visita programada"):
                    service.create_scheduled_visit(sample_visit_data)
    
    def test_create_scheduled_visit_validation_error(self, service, sample_visit_data, mock_repository):
        """Test crear visita con error de validación del modelo"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            with patch.object(service, '_validate_client_exists', return_value=True):
                mock_repository.create.side_effect = ValueError("Error de validación")
                
                with pytest.raises(SalesPlanValidationError):
                    service.create_scheduled_visit(sample_visit_data)
    
    def test_create_scheduled_visit_repository_error(self, service, sample_visit_data, mock_repository):
        """Test crear visita con error de repositorio"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            with patch.object(service, '_validate_client_exists', return_value=True):
                mock_repository.create.side_effect = Exception("Error de BD")
                
                with pytest.raises(SalesPlanBusinessLogicError):
                    service.create_scheduled_visit(sample_visit_data)
    
    def test_get_scheduled_visits_success(self, service, mock_repository):
        """Test obtener visitas programadas exitosamente"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            mock_db_visit = Mock()
            mock_db_visit.id = 'visit1'
            mock_db_visit.date = date(2025, 12, 1)
            
            mock_repository.get_by_seller_with_filters.return_value = [
                (mock_db_visit, 2)
            ]
            
            results = service.get_scheduled_visits('seller1')
            
            assert len(results) == 1
            assert results[0]['id'] == 'visit1'
            assert results[0]['date'] == '01-12-2025'
            assert results[0]['count_clients'] == 2
    
    def test_get_scheduled_visits_with_date_filter(self, service, mock_repository):
        """Test obtener visitas con filtro de fecha"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            mock_db_visit = Mock()
            mock_db_visit.id = 'visit1'
            mock_db_visit.date = date(2025, 12, 1)
            
            mock_repository.get_by_seller_with_filters.return_value = [
                (mock_db_visit, 2)
            ]
            
            results = service.get_scheduled_visits('seller1', visit_date='01-12-2025')
            
            assert len(results) == 1
            mock_repository.get_by_seller_with_filters.assert_called_once()
    
    def test_get_scheduled_visits_seller_not_found(self, service):
        """Test obtener visitas con vendedor inexistente"""
        with patch.object(service, '_validate_seller_exists', return_value=False):
            with pytest.raises(SalesPlanValidationError, match="no existe"):
                service.get_scheduled_visits('seller1')
    
    def test_get_scheduled_visits_invalid_date_format(self, service):
        """Test obtener visitas con formato de fecha inválido"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            with pytest.raises(SalesPlanValidationError, match="formato de fecha"):
                service.get_scheduled_visits('seller1', visit_date='2025-12-01')
    
    def test_get_scheduled_visits_empty_results(self, service, mock_repository):
        """Test obtener visitas sin resultados"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            mock_repository.get_by_seller_with_filters.return_value = []
            
            results = service.get_scheduled_visits('seller1')
            
            assert len(results) == 0
    
    def test_get_scheduled_visits_repository_error(self, service, mock_repository):
        """Test obtener visitas con error de repositorio"""
        with patch.object(service, '_validate_seller_exists', return_value=True):
            mock_repository.get_by_seller_with_filters.side_effect = Exception("Error de BD")
            
            with pytest.raises(SalesPlanBusinessLogicError):
                service.get_scheduled_visits('seller1')
    
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
    def test_validate_client_exists_success(self, mock_get, service):
        """Test validar que cliente existe"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = service._validate_client_exists('client1')
        
        assert result is True
    
    @patch('requests.get')
    def test_validate_client_exists_not_found(self, mock_get, service):
        """Test validar que cliente no existe"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = service._validate_client_exists('client1')
        
        assert result is False
    
    @patch('requests.get')
    def test_validate_client_exists_request_exception(self, mock_get, service):
        """Test validar cliente con excepción de requests"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException()
        
        result = service._validate_client_exists('client1')
        
        assert result is False

