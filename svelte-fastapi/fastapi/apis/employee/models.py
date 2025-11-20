from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String
from database import Base
from sqlalchemy.orm import Mapped, mapped_column

class EmployeeBase(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    employee_name = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False, index=True)
    email = Column(String, index=True)
    is_active = Column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
