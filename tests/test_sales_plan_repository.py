"""
Tests para el repositorio SalesPlanRepository
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.repositories.sales_plan_repository import SalesPlanRepository
from app.models.sales_plan import SalesPlan
from sqlalchemy.exc import SQLAlchemyError


class TestSalesPlanRepository:
    """Tests para el repositorio SalesPlanRepository"""
    
    @pytest.fixture
    def mock_sales_plan_db(self):
        """Mock del modelo de base de datos SalesPlanDB"""
        SalesPlanDB = MagicMock()
        SalesPlanDB.name = Mock()
        SalesPlanDB.client_id = Mock()
        SalesPlanDB.id = Mock()
        return SalesPlanDB
    
    @pytest.fixture
    def mock_session(self, mock_sales_plan_db):
        """Mock de sesión de base de datos"""
        session = Mock()
        
        # Crear una cadena de mocks para query que se mantiene
        chain = Mock()
        chain.filter.return_value = chain
        chain.first.return_value = None
        chain.all.return_value = []
        chain.count.return_value = 0
        chain.offset.return_value = chain
        chain.limit.return_value = chain
        chain.ilike.return_value = chain
        
        # Configurar query para retornar el chain configurado
        query_base = Mock()
        query_base.filter.return_value = chain
        query_base.all.return_value = []
        query_base.count.return_value = 0
        query_base.offset.return_value = chain
        query_base.limit.return_value = chain
        query_base.first.return_value = None
        
        session.query.return_value = query_base
        session.add.return_value = None
        session.commit.return_value = None
        session.rollback.return_value = None
        session.refresh.return_value = None
        session.count.return_value = 0
        session.delete.return_value = None
        
        return session
    
    @pytest.fixture
    def repository(self, mock_session):
        """Repositorio con sesión mockeada"""
        return SalesPlanRepository(mock_session)
    
    @pytest.fixture
    def sample_sales_plan(self):
        """Plan de ventas de muestra"""
        return SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
    
    @patch('app.repositories.sales_plan_repository.SalesPlanDB')
    def test_create_sales_plan_success(self, mock_sales_plan_db, repository, sample_sales_plan, mock_session):
        """Test crear plan exitosamente"""
        mock_sales_plan_db.name = Mock()
        mock_sales_plan_db.return_value.id = 1
        
        repository._db_to_model = Mock(return_value=sample_sales_plan)
        
        result = repository.create(sample_sales_plan)
        
        assert result == sample_sales_plan
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @patch('app.repositories.sales_plan_repository.SalesPlanDB')
    def test_create_sales_plan_duplicate_name(self, mock_sales_plan_db, repository, sample_sales_plan, mock_session):
        """Test crear plan con nombre duplicado"""
        mock_sales_plan_db.name = Mock()
        
        # Simular que ya existe un plan
        existing_plan = Mock()
        existing_plan.name = 'Plan Q1 2025'
        chain = mock_session.query.return_value.filter.return_value
        chain.first.return_value = existing_plan
        
        with pytest.raises(Exception, match="Ya existe un plan"):
            repository.create(sample_sales_plan)
    
    def test_create_sales_plan_database_error(self, repository, sample_sales_plan, mock_session):
        """Test crear plan con error de base de datos"""
        mock_session.add.side_effect = SQLAlchemyError("Error")
        
        with pytest.raises(Exception, match="Error al crear plan"):
            repository.create(sample_sales_plan)
        
        mock_session.rollback.assert_called_once()
    
    def test_get_all_success(self, repository, mock_session):
        """Test obtener todos los planes"""
        mock_db_plan = Mock()
        mock_db_plan.id = 1
        mock_db_plan.name = 'Plan Q1 2025'
        mock_session.query.return_value.all.return_value = [mock_db_plan]
        
        repository._db_to_model = Mock(return_value=SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        ))
        
        result = repository.get_all()
        
        assert len(result) == 1
    
    def test_get_all_database_error(self, repository, mock_session):
        """Test obtener todos con error"""
        mock_session.query.return_value.all.side_effect = SQLAlchemyError("Error")
        
        with pytest.raises(Exception, match="Error al obtener planes"):
            repository.get_all()
    
    def test_get_with_filters_no_filters(self, repository, mock_session):
        """Test obtener con filtros sin filtros"""
        mock_db_plan = Mock()
        mock_db_plan.id = 1
        mock_db_plan.name = 'Plan Q1 2025'
        mock_db_plan.start_date = datetime(2025, 1, 1)
        mock_db_plan.end_date = datetime(2025, 3, 31)
        mock_db_plan.client_id = 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        mock_db_plan.target_revenue = 150000.50
        mock_db_plan.objectives = ''
        
        # Configurar query_base directamente ya que no hay filtros
        mock_session.query.return_value.count.return_value = 1
        mock_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [mock_db_plan]
        
        repository._db_to_model = Mock(return_value=SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        ))
        
        plans, total = repository.get_with_filters(page=1, per_page=10)
        
        assert total == 1
    
    @patch('app.repositories.sales_plan_repository.SalesPlanDB')
    def test_get_with_filters_with_name(self, mock_sales_plan_db, repository, mock_session):
        """Test obtener con filtro por nombre"""
        mock_sales_plan_db.name = Mock()
        mock_db_plan = Mock()
        mock_db_plan.id = 1
        mock_db_plan.name = 'Plan Q1 2025'
        mock_db_plan.start_date = datetime(2025, 1, 1)
        mock_db_plan.end_date = datetime(2025, 3, 31)
        mock_db_plan.client_id = 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        mock_db_plan.target_revenue = 150000.50
        mock_db_plan.objectives = ''
        
        chain = mock_session.query.return_value.filter.return_value
        chain.all.return_value = [mock_db_plan]
        chain.count.return_value = 1
        
        repository._db_to_model = Mock(return_value=SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        ))
        
        plans, total = repository.get_with_filters(page=1, per_page=10, name='Plan')
        
        assert total == 1
    
    @patch('app.repositories.sales_plan_repository.SalesPlanDB')
    def test_get_with_filters_with_client_id(self, mock_sales_plan_db, repository, mock_session):
        """Test obtener con filtro por client_id"""
        mock_sales_plan_db.client_id = Mock()
        mock_db_plan = Mock()
        mock_db_plan.id = 1
        mock_db_plan.name = 'Plan Q1 2025'
        mock_db_plan.start_date = datetime(2025, 1, 1)
        mock_db_plan.end_date = datetime(2025, 3, 31)
        mock_db_plan.client_id = 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        mock_db_plan.target_revenue = 150000.50
        mock_db_plan.objectives = ''
        
        chain = mock_session.query.return_value.filter.return_value
        chain.all.return_value = [mock_db_plan]
        chain.count.return_value = 1
        
        repository._db_to_model = Mock(return_value=SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        ))
        
        plans, total = repository.get_with_filters(
            page=1, 
            per_page=10, 
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        )
        
        assert total == 1
    
    @patch('app.repositories.sales_plan_repository.SalesPlanDB')
    def test_get_with_filters_with_client_ids(self, mock_sales_plan_db, repository, mock_session):
        """Test obtener con filtro por client_ids"""
        mock_db_plan = Mock()
        mock_db_plan.id = 1
        mock_db_plan.name = 'Plan Q1 2025'
        mock_db_plan.start_date = datetime(2025, 1, 1)
        mock_db_plan.end_date = datetime(2025, 3, 31)
        mock_db_plan.client_id = 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        mock_db_plan.target_revenue = 150000.50
        mock_db_plan.objectives = ''
        
        chain = mock_session.query.return_value.filter.return_value
        chain.all.return_value = [mock_db_plan]
        chain.count.return_value = 1
        
        repository._db_to_model = Mock(return_value=SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        ))
        
        plans, total = repository.get_with_filters(
            page=1,
            per_page=10,
            client_ids=['a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b', 'another-id']
        )
        
        assert total == 1
    
    @patch('app.repositories.sales_plan_repository.SalesPlanDB')
    def test_db_to_model(self, mock_sales_plan_db, repository, mock_session):
        """Test conversión DB a modelo"""
        from datetime import datetime
        from app.models.sales_plan import SalesPlan
        
        # Crear mock de entidad DB
        mock_db_plan = Mock()
        mock_db_plan.id = 1
        mock_db_plan.name = 'Test Plan'
        mock_db_plan.start_date = datetime(2025, 1, 1)
        mock_db_plan.end_date = datetime(2025, 3, 31)
        mock_db_plan.client_id = 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
        mock_db_plan.target_revenue = 150000.50
        mock_db_plan.objectives = 'Test objectives'
        mock_db_plan.created_at = datetime.now()
        mock_db_plan.updated_at = datetime.now()
        
        # Ejecutar conversión
        result = repository._db_to_model(mock_db_plan)
        
        # Verificar conversión
        assert isinstance(result, SalesPlan)
        assert result.id == 1
        assert result.name == 'Test Plan'
        assert result.target_revenue == 150000.50
    
    def test_delete_all_success(self, repository, mock_session):
        """Test eliminar todos exitosamente"""
        mock_session.query.return_value.count.return_value = 5
        
        result = repository.delete_all()
        
        assert result == 5
        mock_session.commit.assert_called_once()
    
    def test_delete_all_database_error(self, repository, mock_session):
        """Test eliminar todos con error"""
        mock_session.query.return_value.count.side_effect = SQLAlchemyError("Error")
        
        with pytest.raises(Exception, match="Error al eliminar todos"):
            repository.delete_all()
        
        mock_session.rollback.assert_called_once()
    
    def test_get_with_filters_sqlalchemy_error(self, repository, mock_session):
        """Test obtener con error de SQLAlchemy (líneas 99-100)"""
        from sqlalchemy.exc import SQLAlchemyError
        
        # Hacer que count() lance el error
        chain = mock_session.query.return_value
        chain.count.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception, match="Error al obtener planes de ventas"):
            repository.get_with_filters(page=1, per_page=10)


