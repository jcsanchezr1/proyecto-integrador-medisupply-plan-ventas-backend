"""
Servicio para actualizar clientes de visitas programadas
"""
import logging
from typing import Optional
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError

logger = logging.getLogger(__name__)


class ScheduledVisitUpdateService:
    """Servicio para actualizar clientes en visitas programadas"""
    
    def __init__(self, scheduled_visit_repository: ScheduledVisitRepository):
        logger.info("=== INICIALIZANDO ScheduledVisitUpdateService ===")
        self.scheduled_visit_repository = scheduled_visit_repository
    
    def update_client_visit(
        self, 
        seller_id: str, 
        visit_id: str, 
        client_id: str, 
        find: str,
        filename: Optional[str] = None,
        filename_url: Optional[str] = None
    ) -> dict:
        """Actualiza un cliente específico de una visita"""
        try:
            # Validar que la visita existe y pertenece al vendedor
            visit = self.scheduled_visit_repository.get_by_id_and_seller(visit_id, seller_id)
            if not visit:
                raise SalesPlanValidationError(
                    f"No se encontró la visita con ID {visit_id} para el vendedor {seller_id}"
                )
            
            # Validar que el cliente existe en la visita
            client_visit = self.scheduled_visit_repository.get_client_visit(visit_id, client_id)
            if not client_visit:
                raise SalesPlanValidationError(
                    f"No se encontró el cliente {client_id} en la visita {visit_id}"
                )
            
            # Preparar los datos para actualizar
            update_data = {
                'status': 'COMPLETED',
                'find': find
            }
            
            # Por ahora no guardamos filename ni filename_url (según requerimiento)
            # if filename:
            #     update_data['filename'] = filename
            # if filename_url:
            #     update_data['filename_url'] = filename_url
            
            # Actualizar el registro
            updated = self.scheduled_visit_repository.update_client_visit(
                visit_id, 
                client_id, 
                update_data
            )
            
            if not updated:
                raise SalesPlanBusinessLogicError("No se pudo actualizar el cliente de la visita")
            
            logger.info(f"Cliente {client_id} de visita {visit_id} actualizado exitosamente")
            
            return {
                "visit_id": visit_id,
                "client_id": client_id,
                "status": "COMPLETED",
                "find": find
            }
            
        except SalesPlanValidationError:
            raise
        except Exception as e:
            raise SalesPlanBusinessLogicError(f"Error al actualizar cliente de la visita: {str(e)}")

