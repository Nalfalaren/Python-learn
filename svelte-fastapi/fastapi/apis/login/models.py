from datetime import datetime
from sqlalchemy import Column, DateTime, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class AccountBase(Base):
    __tablename__ = "employee_register_information"

    id = Column(String, primary_key=True, nullable=False, index=True)
    employee_name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    password = Column(String, index=True, nullable=False)
    role = Column(String, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    orders = relationship("OrderBase", back_populates="employee")
    is_active = Column(
        Enum("Active", "Inactive", name="product_status"),
        default="Active",
        nullable=False
    )

    reset_tokens_employee = relationship("PasswordResetTokenEmployeeBase", back_populates="employee")


