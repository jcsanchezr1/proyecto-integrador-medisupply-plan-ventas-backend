"""
Servicio para lógica de negocio del detalle de visitas programadas
"""
import logging
import os
from typing import Optional
import requests
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError

logger = logging.getLogger(__name__)


class ScheduledVisitDetailService:
    """Servicio para obtener detalle completo de visitas programadas"""
    
    def __init__(self, scheduled_visit_repository: ScheduledVisitRepository):
        logger.info("=== INICIALIZANDO ScheduledVisitDetailService ===")
        self.scheduled_visit_repository = scheduled_visit_repository
        self.auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8080')
    
    def get_visit_detail(self, visit_id: str, seller_id: str) -> dict:
        """Obtiene el detalle completo de una visita con información de clientes"""
        try:
            # Validar que el vendedor existe
            if not self._validate_seller_exists(seller_id):
                raise SalesPlanValidationError(f"El vendedor con ID {seller_id} no existe")
            
            # Obtener la visita del repositorio
            visit = self.scheduled_visit_repository.get_by_id_and_seller(visit_id, seller_id)
            
            if not visit:
                raise SalesPlanValidationError(f"No se encontró la visita con ID {visit_id} para el vendedor {seller_id}")
            
            # Obtener información completa de cada cliente
            clients_details = []
            for client in visit.clients:
                client_detail = self._get_client_detail(client.client_id)
                if client_detail:
                    clients_details.append(client_detail)
            
            return {
                "id": visit.id,
                "seller_id": visit.seller_id,
                "date": visit.date.strftime('%d-%m-%Y'),
                "clients": clients_details,
                "created_at": visit.created_at.isoformat() if visit.created_at else None,
                "updated_at": visit.updated_at.isoformat() if visit.updated_at else None
            }
        except SalesPlanValidationError:
            raise
        except Exception as e:
            raise SalesPlanBusinessLogicError(f"Error al obtener detalle de visita: {str(e)}")
    
    def _validate_seller_exists(self, seller_id: str) -> bool:
        """Valida que el vendedor existe en el servicio de autenticador"""
        try:
            response = requests.get(
                f"{self.auth_service_url}/auth/user/{seller_id}",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validando vendedor: {str(e)}")
            return False
    
    def _get_client_detail(self, client_id: str) -> Optional[dict]:
        """Obtiene el detalle completo de un cliente desde el servicio de autenticación"""
        try:
            response = requests.get(
                f"{self.auth_service_url}/auth/user/{client_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # El servicio puede retornar data envuelta en "data" o directamente
                if 'data' in response_data:
                    return response_data['data']
                return response_data
            
            logger.warning(f"No se pudo obtener detalle del cliente {client_id}: Status {response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo detalle del cliente {client_id}: {str(e)}")
            return None

