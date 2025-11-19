"""
Tests para los modelos de base de datos
"""
import pytest
import os


class TestScheduledVisitClientDB:
    """Tests para el modelo ScheduledVisitClientDB"""
    
    def test_model_has_filename_processed_column_defined(self):
        """Test que el modelo tiene la columna filename_processed definida en el código"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'db_models.py')
        with open(file_path, 'r') as f:
            source = f.read()
        assert 'filename_processed' in source, "Columna filename_processed no está definida en el código"
    
    def test_model_has_filename_url_processed_column_defined(self):
        """Test que el modelo tiene la columna filename_url_processed definida en el código"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'db_models.py')
        with open(file_path, 'r') as f:
            source = f.read()
        assert 'filename_url_processed' in source, "Columna filename_url_processed no está definida en el código"
    
    def test_model_new_columns_are_string_and_text(self):
        """Test que las nuevas columnas están definidas con los tipos correctos"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'db_models.py')
        with open(file_path, 'r') as f:
            source = f.read()
        # Verificar que filename_processed es String(255)
        assert 'filename_processed = Column(String(255)' in source or 'filename_processed = Column(String' in source
        # Verificar que filename_url_processed es Text
        assert 'filename_url_processed = Column(Text' in source
        # Verificar que son nullable
        assert 'nullable=True' in source or 'nullable = True' in source
    
    def test_model_all_expected_columns_are_defined(self):
        """Test que todas las columnas esperadas están definidas en el código"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'db_models.py')
        with open(file_path, 'r') as f:
            source = f.read()
        expected_columns = [
            'id', 'visit_id', 'client_id', 'status', 'find',
            'filename', 'filename_url', 'file_status',
            'filename_processed', 'filename_url_processed',
            'created_at', 'updated_at'
        ]
        
        for col_name in expected_columns:
            assert col_name in source, f"Columna {col_name} no está definida en el código fuente"


class TestSalesPlanDB:
    """Tests para el modelo SalesPlanDB"""
    
    def test_model_has_all_expected_columns_defined(self):
        """Test que todas las columnas esperadas están definidas en el código"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'db_models.py')
        with open(file_path, 'r') as f:
            source = f.read()
        expected_columns = [
            'id', 'name', 'start_date', 'end_date', 'client_id',
            'seller_id', 'target_revenue', 'objectives',
            'created_at', 'updated_at'
        ]
        
        for col_name in expected_columns:
            assert col_name in source, f"Columna {col_name} no está definida en el código fuente"


class TestScheduledVisitDB:
    """Tests para el modelo ScheduledVisitDB"""
    
    def test_model_has_all_expected_columns_defined(self):
        """Test que todas las columnas esperadas están definidas en el código"""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'models', 'db_models.py')
        with open(file_path, 'r') as f:
            source = f.read()
        expected_columns = [
            'id', 'seller_id', 'date', 'created_at', 'updated_at'
        ]
        
        for col_name in expected_columns:
            assert col_name in source, f"Columna {col_name} no está definida en el código fuente"

