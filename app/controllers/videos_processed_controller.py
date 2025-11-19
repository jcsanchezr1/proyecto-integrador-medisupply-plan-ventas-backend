"""
Controlador para manejo de videos procesados
"""
import logging
from flask_restful import Resource
from flask import request
from typing import Dict, Any, Tuple
from ..services.videos_processed_service import VideosProcessedService
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository
from .base_controller import BaseController
from ..config.database import auto_close_session

logger = logging.getLogger(__name__)


class VideosProcessedController(BaseController):
    """Controlador para videos procesados"""
    
    def __init__(self):
        logger.debug("Inicializando VideosProcessedController")
        from ..config.database import SessionLocal
        session = SessionLocal()
        self.scheduled_visit_repository = ScheduledVisitRepository(session)
        self.videos_processed_service = VideosProcessedService(self.scheduled_visit_repository)
    
    @auto_close_session
    def get(self):
        """GET /videos-processed - Obtener listado de videos procesados con paginación"""
        logger.info("GET /videos-processed - Iniciando consulta")
        try:
            page = request.args.get('page', type=int, default=1)
            per_page = request.args.get('per_page', type=int, default=10)
            
            if page < 1:
                return self.error_response("Error de validación", "El número de página debe ser mayor a 0", 400)
            
            if per_page < 1 or per_page > 100:
                return self.error_response("Error de validación", "El número de resultados por página debe estar entre 1 y 100", 400)
            
            videos, total = self.videos_processed_service.get_processed_videos(
                page=page,
                per_page=per_page
            )
            
            total_pages = (total + per_page - 1) // per_page if per_page > 0 and total > 0 else (1 if total > 0 else 0)
            data = {
                'videos': videos,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages
                }
            }
            
            return self.success_response(
                data=data,
                message="Videos procesados obtenidos exitosamente"
            )
            
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return self.error_response("Error interno del servidor", str(e), 500)

