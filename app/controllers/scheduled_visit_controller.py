"""
Controlador para manejo de visitas programadas
"""
import logging
from flask_restful import Resource
from flask import request
from typing import Dict, Any, Tuple
from ..services.scheduled_visit_service import ScheduledVisitService
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session

logger = logging.getLogger(__name__)


class ScheduledVisitController(BaseController):
    """Controlador para visitas programadas"""
    
    def __init__(self):
        logger.debug("Inicializando ScheduledVisitController")
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.scheduled_visit_repository = ScheduledVisitRepository(session)
        self.scheduled_visit_service = ScheduledVisitService(self.scheduled_visit_repository)
    
    @auto_close_session
    def post(self, seller_id: str):
        """POST /sellers/{seller_id}/scheduled-visits - Crear visita programada"""
        logger.info(f"POST /sellers/{seller_id}/scheduled-visits - Iniciando creación de visita")
        try:
            # Validar que se recibió un JSON
            if not request.is_json:
                return self.error_response(
                    "Error de validación",
                    "El contenido debe ser JSON",
                    400
                )
            
            # Obtener los datos del body
            data = request.get_json()
            
            # Validar campos obligatorios
            if not data.get('date'):
                return self.error_response(
                    "Error de validación",
                    "El campo 'date' es obligatorio",
                    400
                )
            
            if 'clients' not in data:
                return self.error_response(
                    "Error de validación",
                    "El campo 'clients' es obligatorio",
                    400
                )
            
            if not isinstance(data.get('clients'), list):
                return self.error_response(
                    "Error de validación",
                    "El campo 'clients' debe ser una lista",
                    400
                )
            
            if len(data.get('clients', [])) == 0:
                return self.error_response(
                    "Error de validación",
                    "Debe haber al menos un cliente en la lista",
                    400
                )
            
            # Agregar el seller_id a los datos
            visit_data = {
                'seller_id': seller_id,
                'date': data['date'],
                'clients': data['clients']
            }
            
            # Crear la visita programada
            scheduled_visit = self.scheduled_visit_service.create_scheduled_visit(visit_data)
            
            return self.created_response(
                data=scheduled_visit.to_dict(),
                message="Visita programada creada exitosamente"
            )
            
        except SalesPlanValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except SalesPlanBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return self.error_response("Error interno del servidor", str(e), 500)
    
    @auto_close_session
    def get(self, seller_id: str):
        """GET /sellers/{seller_id}/scheduled-visits - Obtener visitas programadas"""
        logger.info(f"GET /sellers/{seller_id}/scheduled-visits - Iniciando consulta")
        try:
            # Obtener el parámetro de fecha si existe
            visit_date = request.args.get('date', type=str)
            
            # Obtener las visitas programadas
            visits = self.scheduled_visit_service.get_scheduled_visits(
                seller_id=seller_id,
                visit_date=visit_date
            )
            
            return self.success_response(
                data=visits,
                message="Visitas programadas obtenidas exitosamente"
            )
            
        except SalesPlanValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except SalesPlanBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return self.error_response("Error interno del servidor", str(e), 500)

