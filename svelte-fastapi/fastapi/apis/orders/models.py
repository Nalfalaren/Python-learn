from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from database import Base
from sqlalchemy.orm import relationship

class OrderBase(Base):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True, index=True)
    customer_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    status = Column(String, default="PENDING")  
    employee_id = Column(
        String,
        ForeignKey("employees.id"),
        nullable=True
    )
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship("AdminBase", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")