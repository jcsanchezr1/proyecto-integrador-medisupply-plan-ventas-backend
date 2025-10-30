"""
Repositorio para manejo de planes de ventas
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from ..models.sales_plan import SalesPlan
from ..models.db_models import SalesPlanDB
from .base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class SalesPlanRepository(BaseRepository):
    """Repositorio para manejo de planes de ventas"""
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def create(self, sales_plan: SalesPlan) -> SalesPlan:
        """Crea un nuevo plan de ventas"""
        logger.info(f"=== INICIANDO CREACIÓN DE PLAN: {sales_plan.name} ===")
        try:

            existing = self.session.query(SalesPlanDB).filter(
                SalesPlanDB.name == sales_plan.name
            ).first()
            if existing:
                logger.error(f"Nombre duplicado: {sales_plan.name}")
                raise ValueError(f"Ya existe un plan de ventas con el nombre '{sales_plan.name}'")
            
            db_plan = SalesPlanDB(
                name=sales_plan.name,
                start_date=sales_plan.start_date,
                end_date=sales_plan.end_date,
                client_id=sales_plan.client_id,
                seller_id=sales_plan.seller_id,
                target_revenue=sales_plan.target_revenue,
                objectives=sales_plan.objectives
            )
            
            self.session.add(db_plan)
            self.session.commit()
            self.session.refresh(db_plan)
            logger.info(f"Plan creado exitosamente con ID: {db_plan.id}")
            
            return self._db_to_model(db_plan)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al crear plan de ventas: {str(e)}")
    
    def get_all(self) -> List[SalesPlan]:
        """Obtiene todos los planes"""
        try:
            db_plans = self.session.query(SalesPlanDB).all()
            return [self._db_to_model(db_plan) for db_plan in db_plans]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener planes de ventas: {str(e)}")
    
    def get_with_filters(
        self,
        page: int = 1,
        per_page: int = 10,
        name: Optional[str] = None,
        client_id: Optional[str] = None,
        client_ids: Optional[List[str]] = None,
        seller_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[SalesPlan], int]:
        """Obtiene planes con filtros y paginación"""
        try:
            query = self.session.query(SalesPlanDB)
            
            if name:
                query = query.filter(SalesPlanDB.name.ilike(f"%{name}%"))
            
            if seller_id:
                query = query.filter(SalesPlanDB.seller_id == seller_id)
            
            if client_ids:
                query = query.filter(or_(*[SalesPlanDB.client_id == cid for cid in client_ids]))
            elif client_id:
                query = query.filter(SalesPlanDB.client_id == client_id)
            
            if start_date:
                from datetime import datetime
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(SalesPlanDB.start_date >= start)
            
            if end_date:
                from datetime import datetime
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(SalesPlanDB.end_date <= end)
            
            total = query.count()
            
            offset = (page - 1) * per_page
            db_plans = query.offset(offset).limit(per_page).all()
            
            return [self._db_to_model(db_plan) for db_plan in db_plans], total
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener planes de ventas: {str(e)}")
    
    def delete_all(self) -> int:
        """Elimina todos los planes"""
        logger.warning(f"=== ELIMINACIÓN MASIVA DE PLANES ===")
        try:
            count = self.session.query(SalesPlanDB).count()
            self.session.query(SalesPlanDB).delete()
            self.session.commit()
            logger.warning(f"Eliminados {count} planes")
            return count
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error al eliminar todos los planes: {str(e)}")
    

    def get_by_id(self, entity_id: int):  # pragma: no cover
        """No requerido - implementación mínima"""
        pass
    
    def update(self, entity):  # pragma: no cover
        """No requerido - implementación mínima"""
        pass
    
    def delete(self, entity_id: int) -> bool:  # pragma: no cover
        """No requerido - implementación mínima"""
        pass
    
    def _db_to_model(self, db_plan: SalesPlanDB) -> SalesPlan:
        """Convierte modelo de BD a modelo de dominio"""
        return SalesPlan(
            id=db_plan.id,
            name=db_plan.name,
            start_date=db_plan.start_date,
            end_date=db_plan.end_date,
            client_id=db_plan.client_id,
            seller_id=db_plan.seller_id,
            target_revenue=db_plan.target_revenue,
            objectives=db_plan.objectives,
            created_at=db_plan.created_at,
            updated_at=db_plan.updated_at
        )

