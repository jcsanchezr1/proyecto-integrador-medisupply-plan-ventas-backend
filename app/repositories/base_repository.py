"""
Repositorio base para todos los repositorios
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from sqlalchemy.orm import Session


class BaseRepository(ABC):
    """Repositorio base con métodos comunes"""
    
    def __init__(self, session: Session):
        self.session = session
    
    @abstractmethod
    def create(self, entity: Any) -> Any:  # pragma: no cover
        """Crea una nueva entidad"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Any]:  # pragma: no cover
        """Obtiene una entidad por ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Any]:  # pragma: no cover
        """Obtiene todas las entidades"""
        pass
    
    @abstractmethod
    def update(self, entity: Any) -> Any:  # pragma: no cover
        """Actualiza una entidad"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:  # pragma: no cover
        """Elimina una entidad por ID"""
        pass


