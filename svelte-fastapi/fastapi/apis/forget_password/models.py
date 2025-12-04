from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base

class PasswordResetTokenEmployeeBase(Base):
    __tablename__ = "employee_reset_tokens"

    id = Column(String, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    employee = relationship("AdminBase", back_populates="reset_tokens_employee")


class PasswordResetTokenCustomerBase(Base):
    __tablename__ = "customer_reset_tokens"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    client = relationship("CustomerBase", back_populates="reset_tokens_customer")



