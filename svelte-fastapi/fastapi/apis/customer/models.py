from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Enum
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

class CustomerBase(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    customer_name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)
    role = Column(String, nullable=False)
    
    is_active= Column(
        Enum("Active", "Inactive", name="customer_status"),
        default="Inactive",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reset_tokens_customer = relationship("PasswordResetTokenCustomerBase", back_populates="client")
