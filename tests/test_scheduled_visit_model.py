"""
Tests para el modelo ScheduledVisit
"""
import pytest
from datetime import date
from app.models.scheduled_visit import ScheduledVisit, ScheduledVisitClient


class TestScheduledVisitClient:
    """Tests para ScheduledVisitClient"""
    
    def test_create_client_valid(self):
        """Test crear cliente con datos válidos"""
        client = ScheduledVisitClient(client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b')
        assert client.client_id == 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
    
    def test_validate_client_valid(self):
        """Test validar cliente válido"""
        client = ScheduledVisitClient(client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b')
        client.validate()  # No debe lanzar excepción
    
    def test_validate_client_empty_id(self):
        """Test validar cliente sin ID"""
        client = ScheduledVisitClient(client_id='')
        with pytest.raises(ValueError, match="El ID del cliente es obligatorio"):
            client.validate()
    
    def test_validate_client_invalid_uuid(self):
        """Test validar cliente con UUID inválido"""
        client = ScheduledVisitClient(client_id='invalid-uuid')
        with pytest.raises(ValueError, match="El client_id debe ser un UUID válido"):
            client.validate()
    
    def test_to_dict(self):
        """Test convertir cliente a diccionario"""
        client = ScheduledVisitClient(client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b')
        result = client.to_dict()
        assert result == {'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'}


class TestScheduledVisit:
    """Tests para ScheduledVisit"""
    
    @pytest.fixture
    def valid_clients(self):
        """Clientes válidos para testing"""
        return [
            ScheduledVisitClient(client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'),
            ScheduledVisitClient(client_id='b527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b')
        ]
    
    def test_create_visit_valid(self, valid_clients):
        """Test crear visita con datos válidos"""
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=valid_clients
        )
        assert visit.seller_id == 'c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        assert visit.date == date(2025, 12, 1)
        assert len(visit.clients) == 2
        assert visit.id is not None  # Se genera automáticamente
    
    def test_validate_visit_valid(self, valid_clients):
        """Test validar visita válida"""
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=valid_clients
        )
        visit.validate()  # No debe lanzar excepción
    
    def test_validate_empty_seller_id(self, valid_clients):
        """Test validar visita sin seller_id"""
        visit = ScheduledVisit(
            seller_id='',
            date=date(2025, 12, 1),
            clients=valid_clients
        )
        with pytest.raises(ValueError, match="El ID del vendedor es obligatorio"):
            visit.validate()
    
    def test_validate_invalid_seller_id(self, valid_clients):
        """Test validar visita con seller_id inválido"""
        visit = ScheduledVisit(
            seller_id='invalid-uuid',
            date=date(2025, 12, 1),
            clients=valid_clients
        )
        with pytest.raises(ValueError, match="El seller_id debe ser un UUID válido"):
            visit.validate()
    
    def test_validate_empty_date(self, valid_clients):
        """Test validar visita sin fecha"""
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=None,
            clients=valid_clients
        )
        with pytest.raises(ValueError, match="La fecha es obligatoria"):
            visit.validate()
    
    def test_validate_invalid_date_type(self, valid_clients):
        """Test validar visita con fecha inválida"""
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date='2025-12-01',  # String en vez de date
            clients=valid_clients
        )
        with pytest.raises(ValueError, match="La fecha debe ser un objeto de tipo date"):
            visit.validate()
    
    def test_validate_empty_clients(self):
        """Test validar visita sin clientes"""
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=[]
        )
        with pytest.raises(ValueError, match="Debe haber al menos un cliente en la visita"):
            visit.validate()
    
    def test_validate_none_clients(self):
        """Test validar visita con clientes None"""
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=None
        )
        with pytest.raises(ValueError, match="Debe haber al menos un cliente en la visita"):
            visit.validate()
    
    def test_validate_clients_not_list(self):
        """Test validar visita con clientes que no es lista"""
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients='not-a-list'
        )
        with pytest.raises(ValueError, match="Los clientes deben ser una lista"):
            visit.validate()
    
    def test_validate_clients_invalid_type(self, valid_clients):
        """Test validar visita con cliente de tipo inválido"""
        invalid_clients = valid_clients + ['not-a-client']
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=invalid_clients
        )
        with pytest.raises(ValueError, match="Cada cliente debe ser una instancia de ScheduledVisitClient"):
            visit.validate()
    
    def test_validate_duplicate_clients(self):
        """Test validar visita con clientes duplicados"""
        duplicate_clients = [
            ScheduledVisitClient(client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'),
            ScheduledVisitClient(client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b')  # Duplicado
        ]
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=duplicate_clients
        )
        with pytest.raises(ValueError, match="No puede haber clientes duplicados en la visita"):
            visit.validate()
    
    def test_validate_client_with_invalid_uuid(self):
        """Test validar visita con cliente que tiene UUID inválido"""
        invalid_clients = [
            ScheduledVisitClient(client_id='invalid-uuid')
        ]
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=invalid_clients
        )
        with pytest.raises(ValueError, match="El client_id debe ser un UUID válido"):
            visit.validate()
    
    def test_to_dict(self, valid_clients):
        """Test convertir visita a diccionario"""
        visit = ScheduledVisit(
            id='d527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=valid_clients
        )
        result = visit.to_dict()
        
        assert result['id'] == 'd527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        assert result['seller_id'] == 'c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        assert result['date'] == '01-12-2025'
        assert len(result['clients']) == 2
        assert result['clients'][0]['client_id'] == 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        assert 'created_at' in result
        assert 'updated_at' in result
    
    def test_auto_generate_id(self, valid_clients):
        """Test que se genera automáticamente un ID si no se proporciona"""
        visit = ScheduledVisit(
            seller_id='c527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            date=date(2025, 12, 1),
            clients=valid_clients
        )
        assert visit.id is not None
        assert len(visit.id) == 36  # UUID tiene 36 caracteres con guiones

