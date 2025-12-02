from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from database import Base
from sqlalchemy.orm import relationship
from apis.login.models import AccountBase

class OrderBase(Base):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True, index=True)
    customer_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    status = Column(String, default="PENDING")  # pending, processing, shipped, completed, cancelled
    employee_id = Column(
        String,
        ForeignKey("employee_register_information.id"),
        nullable=True
    )
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship(AccountBase, back_populates="orders")
    items = relationship("OrderItem", back_populates="order")