from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Enum
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apis.orders.models import OrderBase

class EmployeeBase(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    employee_name = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    is_active = Column(
        Enum("Active", "Inactive", name="employee_status"),
        default="Inactive",
        nullable=False
    )
    orders = relationship(OrderBase, back_populates="employee")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
