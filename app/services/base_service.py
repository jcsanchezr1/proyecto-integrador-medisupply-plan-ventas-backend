"""
Servicio base para todos los servicios
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any


class BaseService(ABC):
    """Servicio base con métodos comunes"""
    
    @abstractmethod
    def create(self, data: Any) -> Any:
        """Crea una nueva entidad"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Any]:
        """Obtiene una entidad por ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        """Obtiene todas las entidades"""
        pass
    
    @abstractmethod
    def update(self, entity_id: int, data: Any) -> Optional[Any]:
        """Actualiza una entidad"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Elimina una entidad por ID"""
        pass

