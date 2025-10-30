"""
Tests para base_model
"""
import pytest
from unittest.mock import Mock
from app.models.base_model import BaseModel
from app.models.sales_plan import SalesPlan
from datetime import datetime

TEST_SELLER_ID = '8f1b7d3f-4e3b-4f5e-9b2a-7d2a6b9f1c05'

class TestBaseModel:
    """Tests para BaseModel"""
    
    def test_concrete_implementation(self):
        """Test que SalesPlan implementa correctamente BaseModel"""
        plan = SalesPlan(
            name='Test Plan',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            seller_id=TEST_SELLER_ID,
            target_revenue=150000.50
        )
        
        assert hasattr(plan, 'to_dict')
        assert hasattr(plan, 'validate')
        assert callable(plan.to_dict)
        assert callable(plan.validate)
    
    def test_to_dict_implementation(self):
        """Test que to_dict funciona en implementación concreta"""
        plan = SalesPlan(
            name='Test Plan',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            seller_id=TEST_SELLER_ID,
            target_revenue=150000.50
        )
        
        result = plan.to_dict()
        
        assert isinstance(result, dict)
        assert 'name' in result
        assert result['name'] == 'Test Plan'
    
    def test_validate_implementation(self):
        """Test que validate funciona en implementación concreta"""
        plan = SalesPlan(
            name='Test Plan',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            seller_id=TEST_SELLER_ID,
            target_revenue=150000.50
        )
        
        # No debe lanzar excepción
        plan.validate()
