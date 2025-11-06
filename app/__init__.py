"""
Aplicación principal del sistema de plan de ventas MediSupply
"""
import os  # pragma: no cover
from flask import Flask  # pragma: no cover
from flask_restful import Api  # pragma: no cover
from flask_cors import CORS  # pragma: no cover


def create_app():  # pragma: no cover
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    

    cors = CORS(app)
    

    from .config.database import create_tables
    create_tables()
    

    configure_routes(app)
    
    return app


def configure_routes(app):  # pragma: no cover
    """Configura las rutas de la aplicación"""
    from .controllers.health_controller import HealthCheckView
    from .controllers.sales_plan_controller import SalesPlanController, SalesPlanDeleteAllController
    from .controllers.sales_plan_create_controller import SalesPlanCreateController
    from .controllers.scheduled_visit_controller import ScheduledVisitController
    
    api = Api(app)
    

    api.add_resource(HealthCheckView, '/sales-plan/ping')
    

    api.add_resource(SalesPlanCreateController, '/sales-plan/create')
    api.add_resource(SalesPlanController, '/sales-plan')
    api.add_resource(SalesPlanDeleteAllController, '/sales-plan/delete-all')
    
    # Rutas para visitas programadas
    api.add_resource(ScheduledVisitController, '/sellers/<string:seller_id>/scheduled-visits')
    
    print("Rutas configuradas: /sales-plan/ping, /sales-plan/create, /sales-plan, /sales-plan/delete-all, /sellers/<seller_id>/scheduled-visits")
