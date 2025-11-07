"""
Servicio para actualizar clientes de visitas programadas
"""
import logging
import uuid
from typing import Optional
from werkzeug.datastructures import FileStorage
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository
from ..services.cloud_storage_service import CloudStorageService
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError

logger = logging.getLogger(__name__)


class ScheduledVisitUpdateService:
    """Servicio para actualizar clientes en visitas programadas"""
    
    def __init__(
        self, 
        scheduled_visit_repository: ScheduledVisitRepository,
        cloud_storage_service: CloudStorageService
    ):
        logger.info("=== INICIALIZANDO ScheduledVisitUpdateService ===")
        self.scheduled_visit_repository = scheduled_visit_repository
        self.cloud_storage_service = cloud_storage_service
    
    def update_client_visit(
        self, 
        seller_id: str, 
        visit_id: str, 
        client_id: str, 
        find: str,
        file: Optional[FileStorage] = None
    ) -> dict:
        """Actualiza un cliente específico de una visita y sube el archivo a Cloud Storage si se proporciona"""
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
                'find': find,
                'filename': None,
                'filename_url': None
            }
            
            # Si se proporciona archivo, subirlo a Cloud Storage
            if file and file.filename:
                logger.info(f"Subiendo archivo para cliente {client_id} de visita {visit_id}")
                
                # Generar nombre único para el archivo
                # Extraer nombre base y extensión del archivo original
                original_filename = file.filename
                if '.' in original_filename:
                    file_base = '.'.join(original_filename.split('.')[:-1])
                    file_extension = original_filename.split('.')[-1]
                else:
                    file_base = original_filename
                    file_extension = 'bin'
                
                # Generar nombre único: nombre_base-uuid_completo.extension
                unique_id = uuid.uuid4().hex
                unique_filename = f"{file_base}-{unique_id}.{file_extension}"
                
                # Subir archivo a Cloud Storage
                success, message, url = self.cloud_storage_service.upload_file(file, unique_filename)
                
                if not success:
                    raise SalesPlanBusinessLogicError(f"Error al subir archivo: {message}")
                
                update_data['filename'] = unique_filename
                update_data['filename_url'] = url
                logger.info(f"Archivo subido exitosamente: {unique_filename}")
            
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
                "find": find,
                "filename": update_data['filename'],
                "filename_url": update_data['filename_url']
            }
            
        except SalesPlanValidationError:
            raise
        except Exception as e:
            raise SalesPlanBusinessLogicError(f"Error al actualizar cliente de la visita: {str(e)}")

