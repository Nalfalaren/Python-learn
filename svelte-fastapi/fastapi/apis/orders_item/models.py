from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from apis.orders.models import OrderBase

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"))
    product_id = Column(String, ForeignKey("products.id"))
    product_name = Column(String)
    qty = Column(Integer)
    price = Column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    order = relationship(OrderBase, back_populates="items")
