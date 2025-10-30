"""
Configuración global de pytest para el proyecto de plan de ventas
"""
import pytest
from unittest.mock import MagicMock, Mock
import sys
from datetime import datetime


def pytest_configure(config):
    """Configuración que se ejecuta antes de que se importen los módulos de prueba"""

    mock_requests = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'data': {
            'users': [
                {'id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b', 'name': 'Test Client'}
            ]
        }
    }
    mock_response.status_code = 200
    mock_requests.get.return_value = mock_response
    mock_requests.exceptions.RequestException = Exception

    mock_session = MagicMock()
    mock_session.query.return_value = mock_session
    mock_session.filter.return_value = mock_session
    mock_session.all.return_value = []
    mock_session.first.return_value = None
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.close.return_value = None
    mock_session.refresh.return_value = None
    mock_session.offset.return_value = mock_session
    mock_session.limit.return_value = mock_session
    mock_session.count.return_value = 0
    mock_session.in_transaction.return_value = False
    mock_session.delete.return_value = None
    
    mock_engine = MagicMock()
    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session
    
    # Mock de SQLAlchemy exceptions
    mock_sqlalchemy_exceptions = MagicMock()
    mock_sqlalchemy_exceptions.SQLAlchemyError = Exception
    mock_sqlalchemy_exceptions.IntegrityError = Exception
    
    # Aplicar mocks a sys.modules
    sys.modules['requests'] = mock_requests
    
    # Mock completo de SQLAlchemy
    mock_sqlalchemy = MagicMock()
    mock_sqlalchemy.ext = MagicMock()
    mock_sqlalchemy.ext.declarative = MagicMock()
    mock_sqlalchemy.ext.declarative.declarative_base = MagicMock()
    mock_sqlalchemy.orm = MagicMock()
    mock_sqlalchemy.orm.sessionmaker = mock_sessionmaker
    mock_sqlalchemy.orm.Session = mock_session
    mock_sqlalchemy.exc = mock_sqlalchemy_exceptions
    mock_sqlalchemy.engine = MagicMock()
    mock_sqlalchemy.engine.create_engine = MagicMock(return_value=mock_engine)
    mock_sqlalchemy.Column = MagicMock()
    mock_sqlalchemy.Integer = MagicMock()
    mock_sqlalchemy.String = MagicMock()
    mock_sqlalchemy.DateTime = MagicMock()
    mock_sqlalchemy.Float = MagicMock()
    mock_sqlalchemy.Text = MagicMock()
    mock_sqlalchemy.ForeignKey = MagicMock()
    mock_sqlalchemy.Enum = MagicMock()
    mock_sqlalchemy.relationship = MagicMock()
    mock_sqlalchemy.cascade = MagicMock()
    mock_sqlalchemy.or_ = MagicMock()
    
    sys.modules['sqlalchemy'] = mock_sqlalchemy
    sys.modules['sqlalchemy.ext'] = mock_sqlalchemy.ext
    sys.modules['sqlalchemy.ext.declarative'] = mock_sqlalchemy.ext.declarative
    sys.modules['sqlalchemy.orm'] = mock_sqlalchemy.orm
    sys.modules['sqlalchemy.exc'] = mock_sqlalchemy.exc
    sys.modules['sqlalchemy.engine'] = mock_sqlalchemy.engine


@pytest.fixture
def sample_sales_plan_data():
    """Datos de muestra para un plan de ventas"""
    return {
        'name': 'Plan Q1 2025',
        'start_date': '2025-01-01T00:00:00Z',
        'end_date': '2025-03-31T23:59:59Z',
        'client_id': 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
        'target_revenue': 150000.50,
        'objectives': 'Aumentar ventas en 20%'
    }


@pytest.fixture
def sample_sales_plan_model():
    """Modelo de plan de ventas para testing"""
    from app.models.sales_plan import SalesPlan
    from datetime import datetime
    
    return SalesPlan(
        id=1,
        name='Plan Q1 2025',
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 3, 31),
        client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
        seller_id='b527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
        target_revenue=150000.50,
        objectives='Aumentar ventas en 20%',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_session():
    """Mock de sesión de base de datos"""
    from unittest.mock import MagicMock
    
    session = MagicMock()
    session.query.return_value = session
    session.filter.return_value = session
    session.add.return_value = None
    session.commit.return_value = None
    session.rollback.return_value = None
    session.refresh.return_value = None
    session.close.return_value = None
    session.all.return_value = []
    session.first.return_value = None
    session.count.return_value = 0
    session.delete.return_value = None
    session.in_transaction.return_value = False
    session.offset.return_value = session
    session.limit.return_value = session
    
    return session


@pytest.fixture
def mock_flask_app():
    """Mock de aplicación Flask"""
    from unittest.mock import MagicMock
    
    app = MagicMock()
    app.config = {}
    
    return app




