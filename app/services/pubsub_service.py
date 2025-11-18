"""
Servicio de Google Cloud Pub/Sub para envío de eventos
"""
import os
import json
import logging
from typing import Dict, Any
from datetime import datetime
from google.cloud import pubsub_v1

from ..config.settings import Config

logger = logging.getLogger(__name__)


class PubSubService:
    """Servicio para manejar operaciones con Google Cloud Pub/Sub"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._publisher = None
        
        logger.info(f"PubSubService inicializado - Project: {self.config.GCP_PROJECT_ID}")
    
    @property
    def publisher(self) -> pubsub_v1.PublisherClient:
        """Obtiene el cliente de Pub/Sub Publisher"""
        if self._publisher is None:
            try:
                # Configurar credenciales si están disponibles
                if self.config.GOOGLE_APPLICATION_CREDENTIALS:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.GOOGLE_APPLICATION_CREDENTIALS
                
                self._publisher = pubsub_v1.PublisherClient()
            except Exception as e:
                raise Exception(f"Error al inicializar cliente de Pub/Sub: {str(e)}")
        
        return self._publisher
    
    def publish_message(self, topic_name: str, message_data: Dict[str, Any]) -> str:
        """
        Publica un mensaje en un tópico de Pub/Sub
        
        Args:
            topic_name: Nombre del tópico (sin incluir el path completo)
            message_data: Datos del mensaje a publicar
            
        Returns:
            str: ID del mensaje publicado
            
        Raises:
            Exception: Si hay error al publicar el mensaje
        """
        try:
            # Construir el path completo del tópico
            topic_path = self.publisher.topic_path(self.config.GCP_PROJECT_ID, topic_name)
            
            # Convertir el mensaje a JSON y codificar en bytes
            message_json = json.dumps(message_data)
            message_bytes = message_json.encode('utf-8')
            
            # Publicar mensaje
            future = self.publisher.publish(topic_path, message_bytes)
            message_id = future.result()
            
            logger.info(f"Mensaje publicado exitosamente - Topic: {topic_name}, Message ID: {message_id}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Error al publicar mensaje: {str(e)}")
            raise Exception(f"Error al publicar mensaje en Pub/Sub: {str(e)}")
    
    def publish_video_processing_event(self, scheduled_visit_client_id: int) -> str:
        """
        Publica un evento de procesamiento de video
        
        Args:
            scheduled_visit_client_id: ID del registro de scheduled_visit_clients
            
        Returns:
            str: ID del mensaje publicado
            
        Raises:
            Exception: Si hay error al publicar el evento
        """
        try:
            message_data = {
                'scheduled_visit_client_id': scheduled_visit_client_id,
                'event_type': 'video_processing',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return self.publish_message(
                self.config.PUBSUB_TOPIC_VIDEO_PROCESSING,
                message_data
            )
            
        except Exception as e:
            logger.error(f"Error al publicar evento de procesamiento de video: {str(e)}")
            raise

