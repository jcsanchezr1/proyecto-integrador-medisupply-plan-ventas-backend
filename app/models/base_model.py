"""
Modelo base para todos los modelos
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseModel(ABC):
    """Modelo base con métodos comunes"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        pass
    
    @abstractmethod
    def validate(self) -> None:
        """Valida los datos del modelo"""
        pass

