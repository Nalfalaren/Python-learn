from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, String, Integer
from database import Base
from sqlalchemy.orm import Mapped, mapped_column

class ProductBase(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    product_name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    rating = Column(Float)
    description = Column(String)
    stock= Column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
