"""
Servicio para lógica de negocio de videos procesados
"""
import logging
import os
from typing import List, Dict, Any, Tuple, Optional
import requests
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository

logger = logging.getLogger(__name__)


class VideosProcessedService:
    """Servicio para lógica de negocio de videos procesados"""
    
    def __init__(self, scheduled_visit_repository: ScheduledVisitRepository):
        logger.info("=== INICIALIZANDO VideosProcessedService ===")
        self.scheduled_visit_repository = scheduled_visit_repository
        self.auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8080')
    
    def get_processed_videos(
        self,
        page: int = 1,
        per_page: int = 10,
        visit_id: Optional[str] = None,
        client_name: Optional[str] = None,
        file_status: Optional[str] = None,
        find: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Obtiene el listado de videos procesados con información del cliente, paginación y filtros"""
        try:
            # Si se filtra por nombre de cliente, obtener los client_ids primero
            client_ids = None
            if client_name:
                client_ids = self._get_client_ids_by_name(client_name)
                # Si no se encontraron clientes, retornar lista vacía
                if not client_ids:
                    return [], 0
            
            # Obtener registros de scheduled_visit_clients con paginación y filtros
            db_clients, total = self.scheduled_visit_repository.get_processed_videos(
                page=page,
                per_page=per_page,
                visit_id=visit_id,
                client_ids=client_ids,
                file_status=file_status,
                find=find
            )
            
            # Procesar cada registro y obtener el nombre del cliente
            videos = []
            for db_client in db_clients:
                client_name_result = self._get_client_name(db_client.client_id)
                
                video_data = {
                    'id': db_client.id,
                    'visit_id': db_client.visit_id,
                    'name': client_name_result if client_name_result else "Cliente no disponible",
                    'file_status': db_client.file_status,
                    'find': db_client.find,
                    'filename_url': db_client.filename_url,
                    'filename_url_processed': db_client.filename_url_processed
                }
                videos.append(video_data)
            
            return videos, total
        except Exception as e:
            logger.error(f"Error al obtener videos procesados: {str(e)}")
            raise Exception(f"Error al obtener videos procesados: {str(e)}")
    
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
    
    def _get_client_name(self, client_id: str) -> str:
        """Obtiene el nombre del cliente desde el servicio de autenticación."""
        try:
            response = requests.get(
                f"{self.auth_service_url}/auth/user/{client_id}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                user = data.get('data', {}).get('user') or data.get('data', {})
                return user.get('name') if isinstance(user, dict) else None
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo nombre de cliente {client_id}: {str(e)}")
            return None

