"""
Modelos de base de datos para plan de ventas
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Date
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


class ScheduledVisitDB(Base):
    """Modelo de base de datos para visitas programadas"""
    __tablename__ = 'scheduled_visits'
    
    id = Column(String(36), primary_key=True)
    seller_id = Column(String(36), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScheduledVisitClientDB(Base):
    """Modelo de base de datos para clientes asociados a visitas programadas"""
    __tablename__ = 'scheduled_visit_clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_id = Column(String(36), ForeignKey('scheduled_visits.id', ondelete='CASCADE'), nullable=False)
    client_id = Column(String(36), nullable=False)
    status = Column(String(50), nullable=False)
    find = Column(Text, nullable=True)
    filename = Column(String(255), nullable=True)
    filename_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

