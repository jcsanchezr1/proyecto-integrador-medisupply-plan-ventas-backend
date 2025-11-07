"""
Configuración de la aplicación - Estructura para manejar configuraciones
"""
import os


class Config:
    """Configuración base de la aplicación"""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8080'))

    APP_NAME = 'MediSupply Sales Plan Backend'
    APP_VERSION = '1.0.0'

    # Configuración de Google Cloud Storage
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'soluciones-cloud-2024-02')
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'medisupply-images-bucket')
    BUCKET_FOLDER = os.getenv('BUCKET_FOLDER', 'sales-plan')
    BUCKET_LOCATION = os.getenv('BUCKET_LOCATION', 'us-central1')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # Configuración para URLs firmadas con IAM signBlob
    SIGNING_SERVICE_ACCOUNT_EMAIL = os.getenv('SIGNING_SERVICE_ACCOUNT_EMAIL', '')
    
    # Configuración de tamaño máximo de archivos (10 MB por defecto)
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', str(10 * 1024 * 1024)))


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False


def get_config():
    """Retorna la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()
