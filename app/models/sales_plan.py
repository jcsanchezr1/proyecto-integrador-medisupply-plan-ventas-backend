"""
Modelo de Plan de Ventas
"""
from datetime import datetime
from typing import Optional
import re
from .base_model import BaseModel


class SalesPlan(BaseModel):
    """Modelo de Plan de Ventas"""
    
    def __init__(
        self,
        name: str,
        start_date: datetime,
        end_date: datetime,
        client_id: str,
        target_revenue: float,
        objectives: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        id: Optional[int] = None
    ):
        self.id = id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.client_id = client_id
        self.target_revenue = target_revenue
        self.objectives = objectives or ""
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def validate(self) -> None:
        """Valida los datos del plan de ventas"""
        self._validate_name()
        self._validate_client_id()
        self._validate_dates()
        self._validate_target_revenue()
    
    def _validate_name(self) -> None:
        """Valida el nombre del plan de ventas"""
        if not self.name:
            raise ValueError("El nombre del plan de ventas es obligatorio")
        

        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s-]+$', self.name):
            raise ValueError("El nombre solo puede contener letras, números, espacios y tildes")
        

        if len(self.name) > 255:
            raise ValueError("El nombre no puede exceder 255 caracteres")
    
    def _validate_client_id(self) -> None:
        """Valida el ID del cliente"""
        if not self.client_id:
            raise ValueError("El ID del cliente es obligatorio")
        

        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, self.client_id, re.IGNORECASE):
            raise ValueError("El client_id debe ser un UUID válido")
    
    def _validate_dates(self) -> None:
        """Valida las fechas del plan"""
        if not self.start_date:
            raise ValueError("La fecha de inicio es obligatoria")
        
        if not self.end_date:
            raise ValueError("La fecha de fin es obligatoria")
        

        if self.start_date > self.end_date:
            raise ValueError("La fecha de inicio debe ser menor o igual a la fecha de fin")
    
    def _validate_target_revenue(self) -> None:
        """Valida el target revenue"""
        if self.target_revenue is None:
            raise ValueError("El target_revenue es obligatorio")
        
        if not isinstance(self.target_revenue, (int, float)):
            raise ValueError("El target_revenue debe ser un número")
        
        if self.target_revenue < 0:
            raise ValueError("El target_revenue debe ser mayor o igual a 0")
        

        rounded = round(self.target_revenue, 2)
        if abs(self.target_revenue - rounded) > 0.001:
            raise ValueError("El target_revenue debe tener máximo 2 decimales")
    
    def to_dict(self) -> dict:
        """Convierte el plan de ventas a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'client_id': self.client_id,
            'target_revenue': round(self.target_revenue, 2),
            'objectives': self.objectives,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

