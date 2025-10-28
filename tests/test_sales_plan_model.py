"""
Tests para el modelo SalesPlan
"""
import pytest
from datetime import datetime
from app.models.sales_plan import SalesPlan
from app.exceptions.custom_exceptions import SalesPlanException


class TestSalesPlanModel:
    """Tests para el modelo SalesPlan"""
    
    def test_create_valid_sales_plan(self):
        """Test crear un plan de ventas válido"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        assert plan.name == 'Plan Q1 2025'
        assert plan.target_revenue == 150000.50
        assert plan.client_id == 'a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b'
    
    def test_validate_valid_sales_plan(self):
        """Test validar un plan de ventas válido"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        # No debería lanzar excepción
        plan.validate()
    
    def test_validate_empty_name(self):
        """Test validación de nombre vacío"""
        plan = SalesPlan(
            name='',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        with pytest.raises(ValueError, match="El nombre del plan de ventas es obligatorio"):
            plan.validate()
    
    def test_validate_name_with_invalid_characters(self):
        """Test validación de nombre con caracteres inválidos"""
        plan = SalesPlan(
            name='Plan Q1 2025!!!',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        with pytest.raises(ValueError, match="El nombre solo puede contener"):
            plan.validate()
    
    def test_validate_name_too_long(self):
        """Test validación de nombre muy largo"""
        plan = SalesPlan(
            name='A' * 256,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        with pytest.raises(ValueError, match="El nombre no puede exceder 255 caracteres"):
            plan.validate()
    
    def test_validate_name_with_special_characters_allowed(self):
        """Test validación de nombre con caracteres especiales permitidos"""
        plan = SalesPlan(
            name='Plan Q1 2025 - Clínica del Sol',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        plan.validate()
    
    def test_validate_name_with_tildes(self):
        """Test validación de nombre con tildes"""
        plan = SalesPlan(
            name='Plan de Ópera Español',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        plan.validate()
    
    def test_validate_invalid_client_id_format(self):
        """Test validación de client_id inválido"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='invalid-uuid',
            target_revenue=150000.50
        )
        
        with pytest.raises(ValueError, match="El client_id debe ser un UUID válido"):
            plan.validate()
    
    def test_validate_empty_client_id(self):
        """Test validación de client_id vacío"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='',
            target_revenue=150000.50
        )
        
        with pytest.raises(ValueError, match="El ID del cliente es obligatorio"):
            plan.validate()
    
    def test_validate_dates_start_after_end(self):
        """Test validación de fechas cuando start_date > end_date"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 3, 31),
            end_date=datetime(2025, 1, 1),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        with pytest.raises(ValueError, match="La fecha de inicio debe ser menor o igual a la fecha de fin"):
            plan.validate()
    
    def test_validate_dates_start_equals_end(self):
        """Test validación de fechas cuando start_date == end_date"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 1),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        plan.validate()
    
    def test_validate_negative_target_revenue(self):
        """Test validación de target_revenue negativo"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=-100.0
        )
        
        with pytest.raises(ValueError, match="El target_revenue debe ser mayor o igual a 0"):
            plan.validate()
    
    def test_validate_target_revenue_zero(self):
        """Test validación de target_revenue cero"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=0.0
        )
        
        plan.validate()
    
    def test_validate_target_revenue_more_than_2_decimals(self):
        """Test validación de target_revenue con más de 2 decimales"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.501
        )
        
        with pytest.raises(ValueError, match="El target_revenue debe tener máximo 2 decimales"):
            plan.validate()
    
    def test_validate_target_revenue_exactly_2_decimals(self):
        """Test validación de target_revenue con exactamente 2 decimales"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        plan.validate()
    
    def test_to_dict(self):
        """Test conversión a diccionario"""
        plan = SalesPlan(
            id=1,
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50,
            objectives='Aumentar ventas'
        )
        
        data = plan.to_dict()
        
        assert data['id'] == 1
        assert data['name'] == 'Plan Q1 2025'
        assert data['target_revenue'] == 150000.50
        assert data['objectives'] == 'Aumentar ventas'
        assert 'start_date' in data
        assert 'end_date' in data
    
    def test_validate_missing_start_date(self):
        """Test validación sin fecha de inicio"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=None,
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        with pytest.raises(ValueError, match="fecha de inicio"):
            plan.validate()
    
    def test_validate_missing_end_date(self):
        """Test validación sin fecha de fin"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=None,
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=150000.50
        )
        
        with pytest.raises(ValueError, match="fecha de fin"):
            plan.validate()
    
    def test_validate_missing_target_revenue(self):
        """Test validación sin target_revenue"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue=None
        )
        
        with pytest.raises(ValueError, match="target_revenue es obligatorio"):
            plan.validate()
    
    def test_validate_target_revenue_not_number(self):
        """Test validación con target_revenue no numérico"""
        plan = SalesPlan(
            name='Plan Q1 2025',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
            client_id='a527df89-03f4-4c2c-9d4f-8e6b5c7d3a1b',
            target_revenue='not_a_number'
        )
        
        with pytest.raises(ValueError, match="debe ser un número"):
            plan.validate()



