from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base

class PasswordResetTokenEmployeeBase(Base):
    __tablename__ = "password_reset_token_employee"

    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("employee_register_information.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    employee = relationship("AccountBase", back_populates="reset_tokens_employee")


class PasswordResetTokenCustomerBase(Base):
    __tablename__ = "password_reset_token_customer"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    client = relationship("CustomerBase", back_populates="reset_tokens_customer")



