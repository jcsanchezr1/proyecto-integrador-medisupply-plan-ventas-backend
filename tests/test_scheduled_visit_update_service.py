"""
Tests para el servicio ScheduledVisitUpdateService
"""
import pytest
from unittest.mock import Mock, patch
from datetime import date
from app.services.scheduled_visit_update_service import ScheduledVisitUpdateService
from app.exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError


class TestScheduledVisitUpdateService:
    """Tests para ScheduledVisitUpdateService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del repositorio"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """Servicio con repositorio mockeado"""
        return ScheduledVisitUpdateService(mock_repository)
    
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
    
    def test_init_service(self, mock_repository):
        """Test inicialización del servicio"""
        service = ScheduledVisitUpdateService(mock_repository)
        
        assert service.scheduled_visit_repository == mock_repository

