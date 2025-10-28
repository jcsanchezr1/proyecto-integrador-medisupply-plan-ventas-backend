"""
Servicio para lógica de negocio de planes de ventas
"""
import logging
import os
from typing import List, Optional, Tuple
import requests
from ..models.sales_plan import SalesPlan
from ..repositories.sales_plan_repository import SalesPlanRepository
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError

logger = logging.getLogger(__name__)


class SalesPlanService:
    """Servicio para lógica de negocio de planes de ventas"""
    
    def __init__(self, sales_plan_repository: SalesPlanRepository):
        logger.info("=== INICIALIZANDO SalesPlanService ===")
        self.sales_plan_repository = sales_plan_repository
        self.auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8080')
    
    def create_sales_plan(self, plan_data: dict) -> SalesPlan:
        """Crea un nuevo plan de ventas"""
        logger.info(f"=== INICIANDO CREACIÓN DE PLAN: {plan_data.get('name')} ===")
        

        if not self._validate_client_exists(plan_data['client_id']):
            raise SalesPlanValidationError(f"El cliente con ID {plan_data['client_id']} no existe")
        

        from datetime import datetime
        sales_plan = SalesPlan(
            name=plan_data['name'],
            start_date=datetime.fromisoformat(plan_data['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(plan_data['end_date'].replace('Z', '+00:00')),
            client_id=plan_data['client_id'],
            target_revenue=plan_data['target_revenue'],
            objectives=plan_data.get('objectives', '')
        )
        

        sales_plan.validate()
        

        try:
            created_plan = self.sales_plan_repository.create(sales_plan)
            logger.info(f"Plan creado exitosamente: {created_plan.name}")
            return created_plan
        except ValueError as e:
            raise SalesPlanValidationError(str(e))
        except Exception as e:
            raise SalesPlanBusinessLogicError(f"Error al crear plan de ventas: {str(e)}")
    
    def get_sales_plans(
        self,
        page: int = 1,
        per_page: int = 10,
        name: Optional[str] = None,
        client_id: Optional[str] = None,
        client_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[SalesPlan], int]:
        """Obtiene planes con filtros y paginación"""
        try:
            if client_name:
                client_ids = self._get_client_ids_by_name(client_name)
                plans, total = self.sales_plan_repository.get_with_filters(
                    page=page,
                    per_page=per_page,
                    name=name,
                    client_ids=client_ids,
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                plans, total = self.sales_plan_repository.get_with_filters(
                    page=page,
                    per_page=per_page,
                    name=name,
                    client_id=client_id,
                    start_date=start_date,
                    end_date=end_date
                )
            return plans, total
        except Exception as e:
            raise SalesPlanBusinessLogicError(f"Error al obtener planes de ventas: {str(e)}")
    
    def _get_client_ids_by_name(self, client_name: str) -> List[str]:
        """Obtiene IDs de clientes por nombre"""
        try:
            response = requests.get(
                f"{self.auth_service_url}/auth/user?name={client_name}&role=Cliente",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                users = data.get('data', {}).get('users', [])
                return [user['id'] for user in users]
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error buscando clientes por nombre: {str(e)}")
            return []
    
    def delete_all_sales_plans(self) -> bool:
        """Elimina todos los planes"""
        try:
            count = self.sales_plan_repository.delete_all()
            logger.info(f"Eliminados {count} planes de ventas")
            return True
        except Exception as e:
            raise SalesPlanBusinessLogicError(f"Error al eliminar todos los planes: {str(e)}")
    
    def _validate_client_exists(self, client_id: str) -> bool:
        """Valida que el cliente existe en el servicio de autenticador"""
        try:
            response = requests.get(
                f"{self.auth_service_url}/auth/user/{client_id}",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validando cliente: {str(e)}")
            return False
    

    def create(self, data):
        return self.create_sales_plan(data)
    
    def get_by_id(self, entity_id: int):
        pass
    
    def get_all(self):
        plans, _ = self.get_sales_plans()
        return plans
    
    def update(self, entity_id: int, data):
        pass
    
    def delete(self, entity_id: int) -> bool:
        pass
