"""
Modelos de base de datos para plan de ventas
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class SalesPlanDB(Base):
    """Modelo de base de datos para plan de ventas"""
    __tablename__ = 'sales_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    client_id = Column(String(36), nullable=False)
    seller_id = Column(String(36), nullable=False)
    target_revenue = Column(Float, nullable=False)
    objectives = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

