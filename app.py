"""
Punto de entrada principal de la aplicación
"""
import os
import logging
from app import create_app

logger = logging.getLogger(__name__)

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Configuración para desarrollo local
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting MediSupply Sales Plan Backend on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)

