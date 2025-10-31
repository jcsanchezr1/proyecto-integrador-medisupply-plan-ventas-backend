"""
Excepciones personalizadas del sistema de plan de ventas
"""


class SalesPlanException(Exception):
    """Excepción base para el sistema de plan de ventas"""
    pass


class SalesPlanNotFoundError(SalesPlanException):
    """Excepción cuando no se encuentra un plan de ventas"""
    pass


class SalesPlanValidationError(SalesPlanException):
    """Excepción de validación de plan de ventas"""
    pass


class SalesPlanBusinessLogicError(SalesPlanException):
    """Excepción de lógica de negocio de plan de ventas"""
    pass

