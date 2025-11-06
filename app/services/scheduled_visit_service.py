"""
Servicio para lógica de negocio de visitas programadas
"""
import logging
import os
from typing import List, Optional
from datetime import datetime, date
import requests
from ..models.scheduled_visit import ScheduledVisit, ScheduledVisitClient
from ..repositories.scheduled_visit_repository import ScheduledVisitRepository
from ..exceptions.custom_exceptions import SalesPlanValidationError, SalesPlanBusinessLogicError

logger = logging.getLogger(__name__)


class ScheduledVisitService:
    """Servicio para lógica de negocio de visitas programadas"""
    
    def __init__(self, scheduled_visit_repository: ScheduledVisitRepository):
        logger.info("=== INICIALIZANDO ScheduledVisitService ===")
        self.scheduled_visit_repository = scheduled_visit_repository
        self.auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8080')
    
    def create_scheduled_visit(self, visit_data: dict) -> ScheduledVisit:
        """Crea una nueva visita programada"""
        logger.info(f"=== INICIANDO CREACIÓN DE VISITA PROGRAMADA ===")
        
        try:
            # Validar que el vendedor existe
            if not self._validate_seller_exists(visit_data['seller_id']):
                raise SalesPlanValidationError(f"El vendedor con ID {visit_data['seller_id']} no existe")
            
            # Convertir la fecha del formato DD-MM-YYYY a objeto date
            date_str = visit_data['date']
            try:
                visit_date = datetime.strptime(date_str, '%d-%m-%Y').date()
            except ValueError:
                raise SalesPlanValidationError(f"El formato de fecha '{date_str}' es inválido. Use DD-MM-YYYY")
            
            # Validar que todos los clientes existen
            clients_data = visit_data.get('clients', [])
            if not clients_data or len(clients_data) == 0:
                raise SalesPlanValidationError("Debe haber al menos un cliente en la visita")
            
            clients = []
            for client_data in clients_data:
                client_id = client_data.get('client_id')
                if not client_id:
                    raise SalesPlanValidationError("El client_id es obligatorio para cada cliente")
                
                # Validar que el cliente existe
                if not self._validate_client_exists(client_id):
                    raise SalesPlanValidationError(f"El cliente con ID {client_id} no existe")
                
                clients.append(ScheduledVisitClient(client_id=client_id))
            
            # Crear el modelo de visita programada
            scheduled_visit = ScheduledVisit(
                seller_id=visit_data['seller_id'],
                date=visit_date,
                clients=clients
            )
            
            # Validar el modelo
            scheduled_visit.validate()
            
            # Crear la visita en el repositorio
            created_visit = self.scheduled_visit_repository.create(scheduled_visit)
            logger.info(f"Visita programada creada exitosamente: {created_visit.id}")
            return created_visit
            
        except SalesPlanValidationError:
            raise
        except ValueError as e:
            # Errores de validación del repositorio (como fecha duplicada)
            raise SalesPlanValidationError(str(e))
        except Exception as e:
            raise SalesPlanBusinessLogicError(f"Error al crear visita programada: {str(e)}")
    
    def get_scheduled_visits(
        self,
        seller_id: str,
        visit_date: Optional[str] = None
    ) -> List[dict]:
        """Obtiene visitas programadas de un vendedor con filtros"""
        try:
            # Validar que el vendedor existe
            if not self._validate_seller_exists(seller_id):
                raise SalesPlanValidationError(f"El vendedor con ID {seller_id} no existe")
            
            # Convertir la fecha si se proporciona
            date_filter = None
            if visit_date:
                try:
                    date_filter = datetime.strptime(visit_date, '%d-%m-%Y').date()
                except ValueError:
                    raise SalesPlanValidationError(f"El formato de fecha '{visit_date}' es inválido. Use DD-MM-YYYY")
            
            # Obtener las visitas del repositorio
            visits_with_count = self.scheduled_visit_repository.get_by_seller_with_filters(
                seller_id=seller_id,
                visit_date=date_filter
            )
            
            # Formatear la respuesta
            result = []
            for db_visit, count_clients in visits_with_count:
                result.append({
                    'id': db_visit.id,
                    'date': db_visit.date.strftime('%d-%m-%Y'),
                    'count_clients': count_clients
                })
            
            return result
            
        except SalesPlanValidationError:
            raise
        except Exception as e:
            raise SalesPlanBusinessLogicError(f"Error al obtener visitas programadas: {str(e)}")
    
    def _validate_seller_exists(self, seller_id: str) -> bool:
        """Valida que el vendedor existe en el servicio de autenticación"""
        try:
            response = requests.get(
                f"{self.auth_service_url}/auth/user/{seller_id}",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validando vendedor: {str(e)}")
            return False
    
    def _validate_client_exists(self, client_id: str) -> bool:
        """Valida que el cliente existe en el servicio de autenticación"""
        try:
            response = requests.get(
                f"{self.auth_service_url}/auth/user/{client_id}",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validando cliente: {str(e)}")
            return False
    
    # Métodos heredados de BaseService - implementación mínima
    def create(self, data):
        return self.create_scheduled_visit(data)
    
    def get_by_id(self, entity_id: int):  # pragma: no cover
        pass
    
    def get_all(self):  # pragma: no cover
        pass
    
    def update(self, entity_id: int, data):  # pragma: no cover
        pass
    
    def delete(self, entity_id: int) -> bool:  # pragma: no cover
        pass

