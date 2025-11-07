"""
Controlador para actualizar clientes de visitas programadas
"""
import logging
from flask_restful import Resource
from flask import request
from typing import Dict, Any, Tuple
from ..services.scheduled_visit_update_service import ScheduledVisitUpdateService
from ..services.cloud_storage_service import CloudStorageService
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError
from .base_controller import BaseController
from ..config.database import auto_close_session
from ..config.settings import Config

logger = logging.getLogger(__name__)


class ScheduledVisitUpdateController(BaseController):
    """Controlador para actualizar clientes en visitas programadas"""
    
    def __init__(self):
        logger.debug("Inicializando ScheduledVisitUpdateController")
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.config = Config()
        self.scheduled_visit_repository = ScheduledVisitRepository(session)
        self.cloud_storage_service = CloudStorageService(config=self.config)
        self.scheduled_visit_update_service = ScheduledVisitUpdateService(
            self.scheduled_visit_repository,
            self.cloud_storage_service
        )
    
    def _process_multipart_request(self):
        """Procesa petición multipart/form-data"""
        find = request.form.get('find')
        file = request.files.get('file')
        return find, file
    
    def _process_json_request(self):
        """Procesa petición JSON"""
        try:
            data = request.get_json()
            if not data:
                return None, None
            find = data.get('find')
            return find, None
        except Exception:
            return None, None
    
    @auto_close_session
    def post(self, seller_id: str, visit_id: str, client_id: str):
        """POST /sellers/{seller_id}/route/{visit_id}/client/{client_id} - Actualizar cliente de visita"""
        logger.info(f"POST /sellers/{seller_id}/route/{visit_id}/client/{client_id} - Actualizando cliente")
        try:
            # Determinar tipo de petición
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Procesar petición multipart (con archivo)
                find, file = self._process_multipart_request()
            else:
                # Procesar petición JSON (sin archivo)
                find, file = self._process_json_request()
            
            # Validar que el campo 'find' está presente
            if not find:
                return self.error_response(
                    "Error de validación",
                    "El campo 'find' es obligatorio",
                    400
                )
            
            # Validar tamaño del archivo si se envió
            if file:
                file.seek(0, 2)  # Ir al final del archivo
                file_size = file.tell()  # Obtener el tamaño
                file.seek(0)  # Volver al inicio
                
                if file_size > self.config.MAX_CONTENT_LENGTH:
                    max_size_mb = self.config.MAX_CONTENT_LENGTH / (1024 * 1024)
                    return self.error_response(
                        "Error de validación",
                        f"El archivo excede el tamaño máximo permitido de {max_size_mb:.0f} MB. Tamaño actual: {file_size / (1024 * 1024):.2f} MB",
                        400
                    )
                
                logger.info(f"Archivo recibido: {file.filename}, tamaño: {file_size / 1024:.2f} KB")
            
            # Actualizar el cliente de la visita (el servicio maneja la subida del archivo)
            result = self.scheduled_visit_update_service.update_client_visit(
                seller_id=seller_id,
                visit_id=visit_id,
                client_id=client_id,
                find=find,
                file=file
            )
            
            return self.success_response(
                data=result,
                message="Cliente de visita actualizado exitosamente"
            )
            
        except SalesPlanValidationError as e:
            # Error 404 si no se encuentra la visita o el cliente
            return self.error_response("Error de validación", str(e), 404)
        except SalesPlanBusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 500)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return self.error_response("Error interno del servidor", str(e), 500)

