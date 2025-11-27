from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from database import Base
from sqlalchemy.orm import relationship
from apis.orders.models import OrderBase

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(String, ForeignKey("products.id"))
    product_name = Column(String)
    qty = Column(Integer)
    price = Column(Float)
    order = relationship(OrderBase, back_populates="items")
