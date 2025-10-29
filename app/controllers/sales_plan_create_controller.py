"""
Controlador para creación de planes de ventas
"""
import logging
from flask_restful import Resource
from flask import request
from typing import Dict, Any, Tuple
from ..services.sales_plan_service import SalesPlanService
from ..repositories.sales_plan_repository import SalesPlanRepository
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session

logger = logging.getLogger(__name__)


class SalesPlanCreateController(BaseController, Resource):
    """Controlador para creación de planes de ventas"""
    
    def __init__(self):
        logger.debug("Inicializando SalesPlanCreateController")
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.sales_plan_repository = SalesPlanRepository(session)
        self.sales_plan_service = SalesPlanService(self.sales_plan_repository)
    
    @auto_close_session
    def post(self) -> Tuple[Dict[str, Any], int]:
        """POST /sales-plan/create - Crear un nuevo plan de ventas"""
        logger.info("POST /sales-plan/create - Iniciando creacion de plan")
        try:
            try:
                data = request.get_json()
            except Exception:
                return self.error_response("Error de validación", "Se requiere un cuerpo JSON válido", 422)
            
            if not data:
                return self.error_response("Error de validación", "Se requiere un cuerpo JSON", 422)
            

            if not data.get('name'):
                return self.error_response("Error de validación", "El campo 'name' es obligatorio", 422)
            
            if not data.get('start_date'):
                return self.error_response("Error de validación", "El campo 'start_date' es obligatorio", 422)
            
            if not data.get('end_date'):
                return self.error_response("Error de validación", "El campo 'end_date' es obligatorio", 422)
            
            if not data.get('client_id'):
                return self.error_response("Error de validación", "El campo 'client_id' es obligatorio", 422)
            
            if not data.get('target_revenue'):
                return self.error_response("Error de validación", "El campo 'target_revenue' es obligatorio", 422)
            

            try:
                from datetime import datetime
                start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
                
                if start_date > end_date:
                    return self.error_response("Error de validación", "La fecha de inicio debe ser menor o igual a la fecha de fin", 422)
            except (ValueError, AttributeError):
                return self.error_response("Error de validación", "Las fechas deben tener formato ISO 8601 válido", 422)
            

            if not isinstance(data['target_revenue'], (int, float)) or data['target_revenue'] < 0:
                return self.error_response("Error de validación", "El 'target_revenue' debe ser un número mayor o igual a 0", 422)
            
            logger.debug("Invocando sales_plan_service.create_sales_plan")
            sales_plan = self.sales_plan_service.create_sales_plan(data)
            
            return self.created_response(
                data=sales_plan.to_dict(),
                message="Plan de ventas creado exitosamente"
            )
            
        except SalesPlanValidationError as e:
            return self.error_response("Error de validación", str(e), 422)
        except SalesPlanBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 422)
        except ValueError as e:
            logger.error(f"Error de validación: {str(e)}")
            return self.error_response("Error de validación", str(e), 422)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return self.error_response("Error interno del servidor", str(e), 500)

