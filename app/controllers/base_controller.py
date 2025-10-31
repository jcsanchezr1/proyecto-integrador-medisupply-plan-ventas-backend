"""
Controlador base para todos los controladores
"""
from typing import Any, Dict, Tuple
from flask_restful import Resource


class BaseController(Resource):
    """Controlador base con métodos comunes"""
    
    def success_response(self, data: Any = None, message: str = "Operación exitosa") -> Tuple[Dict[str, Any], int]:
        """Respuesta exitosa estándar"""
        response = {
            "success": True,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response, 200
    
    def error_response(self, message: str, details: str = None, status_code: int = 400) -> Tuple[Dict[str, Any], int]:
        """Respuesta de error estándar"""
        response = {
            "success": False,
            "error": message
        }
        if details:
            response["details"] = details
        return response, status_code
    
    def created_response(self, data: Any, message: str = "Recurso creado exitosamente") -> Tuple[Dict[str, Any], int]:
        """Respuesta para creación exitosa"""
        response = {
            "success": True,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response, 201

