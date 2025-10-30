"""
Tests para los controladores de sales plan
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from flask import Flask
from datetime import datetime
from app.controllers.sales_plan_create_controller import SalesPlanCreateController
from app.controllers.sales_plan_controller import SalesPlanController, SalesPlanDeleteAllController
from app.models.sales_plan import SalesPlan
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError

TEST_SELLER_ID = '8f1b7d3f-4e3b-4f5e-9b2a-7d2a6b9f1c05'


@pytest.fixture
def app():
    """Aplicación Flask para testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


class TestSalesPlanCreateController:
    """Tests para SalesPlanCreateController"""
    
    @patch('app.services.sales_plan_service.SalesPlanService.create_sales_plan')
    @patch('app.services.sales_plan_service.SalesPlanService._validate_client_exists')
    @patch('app.services.sales_plan_service.requests.get')
    def test_post_success(self, mock_get, mock_validate, mock_create, app):
        """Test crear plan exitosamente"""
        # Configurar mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'users': [{'id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}]}}
        mock_get.return_value = mock_response
        mock_validate.return_value = True
        
        mock_plan = Mock(spec=SalesPlan)
        mock_plan.to_dict.return_value = {'id': 1, 'name': 'Plan Q1 2025'}
        mock_plan.name = 'Plan Q1 2025'
        mock_plan.id = 1
        mock_create.return_value = mock_plan
        
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 201
            assert 'data' in response
    
    def test_post_missing_name(self, app):
        """Test crear plan sin nombre"""
        with app.test_request_context(json={
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
            assert 'error' in response
    
    def test_post_missing_start_date(self, app):
        """Test crear plan sin fecha de inicio"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_missing_client_id(self, app):
        """Test crear plan sin client_id"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_invalid_date_format(self, app):
        """Test crear plan con formato de fecha inválido"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': 'invalid-date',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_start_date_after_end_date(self, app):
        """Test crear plan con fecha inicio después de fin"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-03-31T00:00:00Z',
            'end_date': '2025-01-01T00:00:00Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_negative_target_revenue(self, app):
        """Test crear plan con target_revenue negativo"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': -100
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_no_json(self, app):
        """Test crear plan sin JSON"""
        with app.test_request_context():
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_validation_error(self, app):
        """Test crear plan con error de validación"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            controller.sales_plan_service.create_sales_plan = Mock(
                side_effect=SalesPlanValidationError("Error de validación")
            )
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_empty_data(self, app):
        """Test crear plan con data vacío"""
        with app.test_request_context(json={}):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_missing_end_date(self, app):
        """Test crear plan sin end_date"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_missing_target_revenue(self, app):
        """Test crear plan sin target_revenue"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    def test_post_missing_seller_id(self, app):
        """Test crear plan sin seller_id"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'target_revenue': 150000.50
        }):
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
            assert 'seller_id' in str(response.get('details', '')).lower() or 'seller_id' in str(response.get('error', '')).lower()
    
    @patch('app.controllers.sales_plan_create_controller.SalesPlanService')
    def test_post_business_logic_error(self, mock_service_class, app):
        """Test crear plan con error de lógica de negocio"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            mock_service = Mock()
            mock_service.create_sales_plan = Mock(side_effect=SalesPlanBusinessLogicError("Error"))
            mock_service_class.return_value = mock_service
            
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 422
    
    @patch('app.controllers.sales_plan_create_controller.SalesPlanService')
    def test_post_generic_exception(self, mock_service_class, app):
        """Test crear plan con excepción genérica"""
        with app.test_request_context(json={
            'name': 'Plan Q1 2025',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-03-31T23:59:59Z',
            'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            'seller_id': TEST_SELLER_ID,
            'target_revenue': 150000.50
        }):
            mock_service = Mock()
            mock_service.create_sales_plan = Mock(side_effect=Exception("Generic error"))
            mock_service_class.return_value = mock_service
            
            controller = SalesPlanCreateController()
            
            response, status = controller.post()
            
            assert status == 500


class TestSalesPlanController:
    """Tests para SalesPlanController"""
    
    def test_get_success(self, app):
        """Test obtener planes exitosamente"""
        with app.test_request_context():
            controller = SalesPlanController()
            
            mock_plan = Mock(spec=SalesPlan)
            mock_plan.to_dict.return_value = {'id': 1, 'name': 'Plan Q1 2025'}
            controller.sales_plan_service.get_sales_plans = Mock(return_value=([mock_plan], 1))
            
            response, status = controller.get()
            
            assert status == 200
            assert 'data' in response
    
    def test_get_with_pagination(self, app):
        """Test obtener planes con paginación"""
        with app.test_request_context('?page=1&per_page=5'):
            controller = SalesPlanController()
            
            mock_plan = Mock(spec=SalesPlan)
            mock_plan.to_dict.return_value = {'id': 1, 'name': 'Plan Q1 2025'}
            controller.sales_plan_service.get_sales_plans = Mock(return_value=([mock_plan], 10))
            
            response, status = controller.get()
            
            assert status == 200
    
    @patch('app.controllers.sales_plan_controller.SalesPlanService')
    def test_get_with_filters(self, mock_service_class, app):
        """Test obtener planes con filtros"""
        with app.test_request_context('?name=Q1&client_id=test'):
            mock_plan = Mock(spec=SalesPlan)
            mock_plan.to_dict.return_value = {'id': 1, 'name': 'Plan Q1 2025'}
            mock_plan.name = 'Plan Q1 2025'
            
            mock_service = Mock()
            mock_service.get_sales_plans = Mock(return_value=([mock_plan], 1))
            mock_service_class.return_value = mock_service
            
            controller = SalesPlanController()
            
            response, status = controller.get()
            
            assert status == 200
    
    def test_get_invalid_page(self, app):
        """Test obtener con página inválida"""
        with app.test_request_context('?page=0'):
            controller = SalesPlanController()
            
            response, status = controller.get()
            
            assert status == 400
    
    def test_get_invalid_per_page_too_large(self, app):
        """Test obtener con per_page muy grande"""
        with app.test_request_context('?per_page=101'):
            controller = SalesPlanController()
            
            response, status = controller.get()
            
            assert status == 400
    
    @patch('app.controllers.sales_plan_controller.SalesPlanService')
    def test_get_business_error(self, mock_service_class, app):
        """Test obtener con error de negocio"""
        with app.test_request_context():
            mock_service = Mock()
            mock_service.get_sales_plans = Mock(side_effect=SalesPlanBusinessLogicError("Error"))
            mock_service_class.return_value = mock_service
            
            controller = SalesPlanController()
            
            response, status = controller.get()
            
            assert status == 500
    
    @patch('app.controllers.sales_plan_controller.SalesPlanService')
    def test_get_validation_error(self, mock_service_class, app):
        """Test obtener con error de validación"""
        with app.test_request_context():
            mock_service = Mock()
            mock_service.get_sales_plans = Mock(side_effect=SalesPlanValidationError("Error"))
            mock_service_class.return_value = mock_service
            
            controller = SalesPlanController()
            
            response, status = controller.get()
            
            assert status == 400
    
    @patch('app.controllers.sales_plan_controller.SalesPlanService')
    def test_get_generic_exception(self, mock_service_class, app):
        """Test obtener con excepción genérica"""
        with app.test_request_context():
            mock_service = Mock()
            mock_service.get_sales_plans = Mock(side_effect=Exception("Generic error"))
            mock_service_class.return_value = mock_service
            
            controller = SalesPlanController()
            
            response, status = controller.get()
            
            assert status == 500


class TestSalesPlanDeleteAllController:
    """Tests para SalesPlanDeleteAllController"""
    
    def test_delete_success(self, app):
        """Test eliminar todos exitosamente"""
        with app.test_request_context():
            controller = SalesPlanDeleteAllController()
            controller.sales_plan_service.delete_all_sales_plans = Mock(return_value=True)
            
            response, status = controller.delete()
            
            assert status == 200
    
    @patch('app.controllers.sales_plan_controller.SalesPlanService')
    def test_delete_business_error(self, mock_service_class, app):
        """Test eliminar con error"""
        with app.test_request_context():
            mock_service = Mock()
            mock_service.delete_all_sales_plans = Mock(side_effect=SalesPlanBusinessLogicError("Error"))
            mock_service_class.return_value = mock_service
            
            controller = SalesPlanDeleteAllController()
            
            response, status = controller.delete()
            
            assert status == 500
    
    @patch('app.controllers.sales_plan_controller.SalesPlanService')
    def test_delete_generic_exception(self, mock_service_class, app):
        """Test eliminar con excepción genérica"""
        with app.test_request_context():
            mock_service = Mock()
            mock_service.delete_all_sales_plans = Mock(side_effect=Exception("Generic error"))
            mock_service_class.return_value = mock_service
            
            controller = SalesPlanDeleteAllController()
            
            response, status = controller.delete()
            
            assert status == 500


