"""
Controlador para manejo de planes de ventas
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


class SalesPlanController(BaseController):
    """Controlador para planes de ventas"""
    
    def __init__(self):
        logger.debug("Inicializando SalesPlanController")
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.sales_plan_repository = SalesPlanRepository(session)
        self.sales_plan_service = SalesPlanService(self.sales_plan_repository)
    
    @auto_close_session
    def get(self):
        """GET /sales-plan - Obtener planes con filtros y paginación"""
        logger.info("GET /sales-plan - Iniciando consulta")
        try:

            page = request.args.get('page', type=int, default=1)
            per_page = request.args.get('per_page', type=int, default=10)
            name = request.args.get('name', type=str)
            client_id = request.args.get('client_id', type=str)
            client_name = request.args.get('client_name', type=str)
            seller_id = request.args.get('seller_id', type=str)
            start_date = request.args.get('start_date', type=str)
            end_date = request.args.get('end_date', type=str)
            
            if page < 1:
                return self.error_response("Error de validación", "El número de página debe ser mayor a 0", 400)
            
            if per_page < 1 or per_page > 100:
                return self.error_response("Error de validación", "El número de resultados por página debe estar entre 1 y 100", 400)
            
            plans, total = self.sales_plan_service.get_sales_plans(
                page=page,
                per_page=per_page,
                name=name,
                client_id=client_id,
                client_name=client_name,
                seller_id=seller_id,
                start_date=start_date,
                end_date=end_date
            )
            

            client_ids = [plan.client_id for plan in plans]
            seller_ids = [plan.seller_id for plan in plans]
            client_names_map = self.sales_plan_service.get_client_names_for_ids(client_ids)
            seller_names_map = self.sales_plan_service.get_seller_names_for_ids(seller_ids)

            items = []
            for plan in plans:
                item = plan.to_dict()
                item['client_name'] = client_names_map.get(plan.client_id)
                item['seller_name'] = seller_names_map.get(plan.seller_id)
                items.append(item)

            total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
            data = {
                'items': items,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages
                }
            }
            
            return self.success_response(
                data=data,
                message="Planes de ventas obtenidos exitosamente"
            )
            
        except SalesPlanValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except SalesPlanBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return self.error_response("Error interno del servidor", str(e), 500)


class SalesPlanDeleteAllController(BaseController):
    """Controlador para eliminar todos los planes de ventas"""
    
    def __init__(self):
        logger.debug("Inicializando SalesPlanDeleteAllController")
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.sales_plan_repository = SalesPlanRepository(session)
        self.sales_plan_service = SalesPlanService(self.sales_plan_repository)
    
    @auto_close_session
    def delete(self):
        """DELETE /sales-plan/delete-all - Eliminar todos los planes"""
        logger.warning("DELETE /sales-plan/delete-all - Iniciando eliminación masiva")
        try:
            self.sales_plan_service.delete_all_sales_plans()
            
            return self.success_response(
                message="Todos los planes de ventas han sido eliminados exitosamente"
            )
            
        except SalesPlanBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return self.error_response("Error interno del servidor", str(e), 500)

