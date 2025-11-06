"""
Controlador para obtener detalle de visitas programadas
"""
import logging
from flask_restful import Resource
from flask import request
from typing import Dict, Any, Tuple
from ..services.scheduled_visit_detail_service import ScheduledVisitDetailService
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session

logger = logging.getLogger(__name__)


class ScheduledVisitDetailController(BaseController):
    """Controlador para detalle de visitas programadas"""
    
    def __init__(self):
        logger.debug("Inicializando ScheduledVisitDetailController")
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.scheduled_visit_repository = ScheduledVisitRepository(session)
        self.scheduled_visit_detail_service = ScheduledVisitDetailService(self.scheduled_visit_repository)
    
    @auto_close_session
    def get(self, seller_id: str, visit_id: str):
        """GET /sellers/{seller_id}/route/{visit_id} - Obtener detalle de visita"""
        logger.info(f"GET /sellers/{seller_id}/route/{visit_id} - Iniciando consulta de detalle")
        try:
            # Obtener el detalle completo de la visita
            visit_detail = self.scheduled_visit_detail_service.get_visit_detail(visit_id, seller_id)
            
            return self.success_response(
                data=visit_detail,
                message="Detalle de visita obtenido exitosamente"
            )
            
        except SalesPlanValidationError as e:
            return self.error_response("Error de validación", str(e), 404)
        except SalesPlanBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return self.error_response("Error interno del servidor", str(e), 500)

