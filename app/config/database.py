"""
Configuración de base de datos
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .settings import get_config

logger = logging.getLogger(__name__)

config = get_config()


DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://medisupply_local_user:medisupply_local_password@localhost:5432/medisupply_local_db')


engine = create_engine(DATABASE_URL, echo=config.DEBUG)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():  # pragma: no cover
    """Obtiene una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():  # pragma: no cover
    """Crea las tablas en la base de datos"""
    from ..models.db_models import Base
    Base.metadata.create_all(bind=engine)

def auto_close_session(func):
    """Decorador que automáticamente cierra la sesión después de ejecutar el método"""
    def wrapper(self, *args, **kwargs):
        import traceback
        

        endpoint_name = f"{func.__name__}"
        if hasattr(self, '__class__'):
            endpoint_name = f"{self.__class__.__name__}.{func.__name__}"
        
        logger.info(f"=== INICIANDO TRANSACCIÓN: {endpoint_name} ===")

        is_mocked = False
        if hasattr(self, 'sales_plan_service'):
            service_class = self.sales_plan_service.__class__
            is_mocked = 'mock' in service_class.__module__.lower() or 'Mock' in service_class.__name__

        if is_mocked:
            logger.debug("Servicio mockeado detectado, saltando recreacion en decorador")
            return func(self, *args, **kwargs)

        if hasattr(self, 'sales_plan_repository') and hasattr(self.sales_plan_repository, 'session'):
            try:
                self.sales_plan_repository.session.close()
                logger.debug("Sesion cerrada en decorador")
            except Exception as e:  # pragma: no cover
                logger.warning(f"Error cerrando sesion existente: {e}")

        session = SessionLocal()
        transaction_started = False
        try:
            from ..repositories.sales_plan_repository import SalesPlanRepository
            from ..services.sales_plan_service import SalesPlanService
            
            self.sales_plan_repository = SalesPlanRepository(session)
            self.sales_plan_service = SalesPlanService(self.sales_plan_repository)
            
            logger.info(f"Nueva sesión creada para {endpoint_name}")
            

            if session.in_transaction():
                transaction_started = True
                logger.info(f"Transacción iniciada automáticamente para {endpoint_name}")

            result = func(self, *args, **kwargs)
            

            if session.in_transaction():
                logger.info(f"Transacción pendiente detectada en {endpoint_name} - haciendo commit explícito")
                session.commit()
                logger.info(f"Commit exitoso para {endpoint_name}")
            else:
                logger.info(f"No hay transacciones pendientes en {endpoint_name}")
            
            logger.info(f"=== TRANSACCIÓN EXITOSA: {endpoint_name} ===")
            return result
            
        except Exception as e:
            logger.error(f"=== ERROR EN TRANSACCIÓN: {endpoint_name} ===")
            logger.error(f"Error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            if session.in_transaction():
                logger.warning(f"Transacción pendiente detectada en {endpoint_name} - haciendo rollback por error")
                try:
                    session.rollback()
                    logger.warning(f"Rollback ejecutado para {endpoint_name}")
                except Exception as rollback_error:
                    logger.error(f"Error durante rollback en {endpoint_name}: {rollback_error}")
            else:
                logger.info(f"No hay transacciones pendientes para hacer rollback en {endpoint_name}")
            
            raise
            
        finally:
            try:

                if session.in_transaction():
                    logger.warning(f"ATENCIÓN: Sesión cerrada con transacción pendiente en {endpoint_name}")
                else:
                    logger.info(f"Sesión cerrada limpiamente para {endpoint_name}")
                
                session.close()
                logger.debug(f"Sesión cerrada en finally para {endpoint_name}")
            except Exception as e:
                logger.error(f"Error cerrando sesión en finally para {endpoint_name}: {e}")
    
    return wrapper


