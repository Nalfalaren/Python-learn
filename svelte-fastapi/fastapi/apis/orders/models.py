from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from database import Base
from sqlalchemy.orm import relationship

class OrderBase(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    status = Column(String, default="PENDING")  # pending, processing, shipped, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("OrderItem", back_populates="order")