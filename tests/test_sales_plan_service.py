"""
Tests para el servicio SalesPlanService
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.services.sales_plan_service import SalesPlanService
from app.repositories.sales_plan_repository import SalesPlanRepository
from app.models.sales_plan import SalesPlan
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


class TestSalesPlanService:
    """Tests para el servicio SalesPlanService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio"""
        return Mock(spec=SalesPlanRepository)
    
    @pytest.fixture
    def sales_plan_service(self, mock_repository):
        """Servicio con repositorio mockeado"""
        return SalesPlanService(mock_repository)
    
    @pytest.fixture
    def sample_data(self):
        """Datos de muestra"""
        return {
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'target_revenue': 150000.50,
            'objectives': 'Aumentar ventas'
        }
    
    def test_create_sales_plan_success(self, sales_plan_service, sample_data):
        """Test crear plan de ventas exitosamente"""
        with patch.object(sales_plan_service, '_validate_client_exists', return_value=True):
            mock_plan = Mock(spec=SalesPlan)
            mock_plan.to_dict.return_value = {'id': 1, 'name': 'Plan Q1 2025'}
            mock_plan.name = 'Plan Q1 2025'
            sales_plan_service.sales_plan_repository.create.return_value = mock_plan
            
            result = sales_plan_service.create_sales_plan(sample_data)
            
            assert result == mock_plan
            sales_plan_service.sales_plan_repository.create.assert_called_once()
    
    def test_create_sales_plan_client_not_found(self, sales_plan_service, sample_data):
        """Test crear plan con cliente inexistente"""
        with patch.object(sales_plan_service, '_validate_client_exists', return_value=False):
            with pytest.raises(SalesPlanValidationError, match="no existe"):
                sales_plan_service.create_sales_plan(sample_data)
    
    def test_create_sales_plan_validation_error(self, sales_plan_service, sample_data):
        """Test crear plan con error de validación"""
        with patch.object(sales_plan_service, '_validate_client_exists', return_value=True):
            sales_plan_service.sales_plan_repository.create.side_effect = ValueError("Nombre inválido")
            
            with pytest.raises(SalesPlanValidationError):
                sales_plan_service.create_sales_plan(sample_data)
    
    def test_create_sales_plan_business_error(self, sales_plan_service, sample_data):
        """Test crear plan con error de negocio"""
        with patch.object(sales_plan_service, '_validate_client_exists', return_value=True):
            sales_plan_service.sales_plan_repository.create.side_effect = Exception("Error de BD")
            
            with pytest.raises(SalesPlanBusinessLogicError):
                sales_plan_service.create_sales_plan(sample_data)
    
    @patch('requests.get')
    def test_validate_client_exists_success(self, mock_get, sales_plan_service):
        """Test validar que cliente existe"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = sales_plan_service._validate_client_exists('test-uuid')
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_validate_client_exists_not_found(self, mock_get, sales_plan_service):
        """Test validar que cliente no existe"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = sales_plan_service._validate_client_exists('test-uuid')
        
        assert result is False
    
    @patch('requests.get')
    def test_validate_client_exists_request_exception(self, mock_get, sales_plan_service):
        """Test validar cliente con excepción de requests"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException()
        
        result = sales_plan_service._validate_client_exists('test-uuid')
        
        assert result is False
    
    @patch('requests.get')
    def test_get_client_ids_by_name_success(self, mock_get, sales_plan_service):
        """Test obtener IDs de clientes por nombre"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'users': [
                    {'id': 'uuid1'},
                    {'id': 'uuid2'}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = sales_plan_service._get_client_ids_by_name('Test Client')
        
        assert result == ['uuid1', 'uuid2']
    
    @patch('requests.get')
    def test_get_client_ids_by_name_empty(self, mock_get, sales_plan_service):
        """Test obtener IDs con respuesta vacía"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'users': []}}
        mock_get.return_value = mock_response
        
        result = sales_plan_service._get_client_ids_by_name('Test Client')
        
        assert result == []
    
    @patch('requests.get')
    def test_get_client_ids_by_name_request_exception(self, mock_get, sales_plan_service):
        """Test obtener IDs con excepción de requests"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException()
        
        result = sales_plan_service._get_client_ids_by_name('Test Client')
        
        assert result == []
    
    def test_get_sales_plans_without_filters(self, sales_plan_service):
        """Test obtener planes sin filtros"""
        mock_plans = [Mock(spec=SalesPlan)]
        sales_plan_service.sales_plan_repository.get_with_filters.return_value = (mock_plans, 1)
        
        plans, total = sales_plan_service.get_sales_plans()
        
        assert plans == mock_plans
        assert total == 1
    
    def test_get_sales_plans_with_client_name(self, sales_plan_service):
        """Test obtener planes con filtro por nombre de cliente"""
        with patch.object(sales_plan_service, '_get_client_ids_by_name', return_value=['uuid1']):
            mock_plans = [Mock(spec=SalesPlan)]
            sales_plan_service.sales_plan_repository.get_with_filters.return_value = (mock_plans, 1)
            
            plans, total = sales_plan_service.get_sales_plans(client_name='Test')
            
            sales_plan_service.sales_plan_repository.get_with_filters.assert_called_once()
            assert plans == mock_plans
    
    def test_get_sales_plans_with_filters(self, sales_plan_service):
        """Test obtener planes con filtros"""
        mock_plans = [Mock(spec=SalesPlan)]
        sales_plan_service.sales_plan_repository.get_with_filters.return_value = (mock_plans, 1)
        
        plans, total = sales_plan_service.get_sales_plans(
            page=1,
            per_page=10,
            name='Plan',
            client_id='uuid',
            start_date='2025-01-01',
            end_date='2025-12-31'
        )
        
        assert plans == mock_plans
        sales_plan_service.sales_plan_repository.get_with_filters.assert_called_once()
    
    def test_get_sales_plans_error(self, sales_plan_service):
        """Test obtener planes con error"""
        sales_plan_service.sales_plan_repository.get_with_filters.side_effect = Exception("Error")
        
        with pytest.raises(SalesPlanBusinessLogicError):
            sales_plan_service.get_sales_plans()
    
    def test_delete_all_sales_plans_success(self, sales_plan_service):
        """Test eliminar todos los planes exitosamente"""
        sales_plan_service.sales_plan_repository.delete_all.return_value = 5
        
        result = sales_plan_service.delete_all_sales_plans()
        
        assert result is True
        sales_plan_service.sales_plan_repository.delete_all.assert_called_once()
    
    def test_delete_all_sales_plans_error(self, sales_plan_service):
        """Test eliminar todos los planes con error"""
        sales_plan_service.sales_plan_repository.delete_all.side_effect = Exception("Error")
        
        with pytest.raises(SalesPlanBusinessLogicError):
            sales_plan_service.delete_all_sales_plans()


