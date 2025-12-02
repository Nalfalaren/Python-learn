import base64
import json
from typing import Annotated
from fastapi import APIRouter, HTTPException, Header, Query, Depends
from sqlalchemy.orm import Session
import uuid
from auth import get_current_user, require_admin, require_employee
from role import StatusCode
from datetime import datetime
from apis.login.models import AccountBase
import logging
from .schema import EmployeeSchema, SuccessMessageSchema, EmployeeInputSchema, SavingEmployeeUpdateSchema
from sqlalchemy.orm import Session
from database import SessionLocal
from sqlalchemy.orm import load_only
router = APIRouter(tags=["Employees"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/me")
def get_account(current_user: dict = Depends(get_current_user)):
    return current_user
    
#Get and search employee
@router.get("/employees")
def search_employee(
    search_id: str | None = Query(None, description="Search by ID"),
    search_employee: str | None = Query(None, description="Search by Employee Name"),
    role: str | None = Query(None, description="Search by role"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    next_cursor: str | None = Query(None, description="Pagination cursor"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_employee),
):
    # --- Decode next_cursor if provided ---
    decoded_cursor = None
    if next_cursor:
        try:
            decoded_json = base64.b64decode(next_cursor).decode("utf-8")
            decoded_cursor = json.loads(decoded_json)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid cursor: {str(e)}")

    query = db.query(AccountBase).options(
    load_only(
        AccountBase.id,
        AccountBase.employee_name,
        AccountBase.email,
        AccountBase.role,
        AccountBase.is_active
    )
)
    if role:
        query = query.filter(AccountBase.role.contains(role))
    elif search_id:
        query = query.filter(AccountBase.id.contains(search_id))
    elif search_employee:
        query = query.filter(AccountBase.employee_name.contains(search_employee))

    
    # Cursor-based pagination logic
    if decoded_cursor:
        last_date = decoded_cursor.get("date")
        last_id = decoded_cursor.get("id")

        # Only add this if both exist
        if last_date and last_id:
            query = query.filter(
                (AccountBase.created_at < last_date)
                | ((AccountBase.created_at == last_date) & (AccountBase.id < last_id))
            )

    # Sort newest first
    query = query.order_by(AccountBase.created_at.desc(), AccountBase.id.desc())
    
    # Get paginated results
    employees = query.limit(limit).all()
    total_employee = db.query(AccountBase).count()

    # --- Compute next_cursor ---
    next_cursor_value = None
    if employees:
        last = employees[-1]
        next_cursor_obj = {
            "date": last.created_at.isoformat() if last.created_at else None,
            "id": last.id,
        }
        encoded_cursor = base64.b64encode(
            json.dumps(next_cursor_obj).encode("utf-8")
        ).decode("utf-8")
        next_cursor_value = encoded_cursor

    # --- Return response ---
    return {
        "message": "Search successfully",
        "search_result": employees,
        "employee_count": len(employees),
        "total_employee": total_employee,
        "next_cursor": next_cursor_value,
    }

#Get detail employee
@router.get('/employee/{employeeId}', response_model=EmployeeSchema)
def get_employee_detail(employeeId: str, db: Session = Depends(get_db), _: dict = Depends(require_admin),):
    employee = db.query(AccountBase).filter(AccountBase.id == employeeId).first()
    if not employee:
        raise HTTPException(status_code=404, detail='Employee not existed!')
    return employee
    
@router.post('/employees', response_model=SuccessMessageSchema)
def create_employee(employee: EmployeeInputSchema, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    new_employee = AccountBase(
        id=str(uuid.uuid4()),
        employee_name = employee.employee_name,
        role = employee.role,
        email = employee.email,
        is_active = employee.is_active,
        created_at=datetime.utcnow()
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return SuccessMessageSchema(message='employee created successfully')

@router.delete('/employee/{employeeId}', response_model=SuccessMessageSchema)
def delete_employee(employeeId: str, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    delete_user = db.query(AccountBase).filter(AccountBase.id == employeeId).first()
    if delete_user:
        db.delete(delete_user)
        db.commit()
        return {'message': 'employee deleted successfully'}
    raise HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail='Employee not existed!')

@router.put('/employee/{employeeId}', response_model=SuccessMessageSchema)
def update_employee(
    employeeId: str,
    employee_update_data: SavingEmployeeUpdateSchema,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    update_user = db.query(AccountBase).filter(AccountBase.id == employeeId).first()
    if not update_user:
        raise HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail='Employee not existed!')
    
    # Update giá trị vào SQLAlchemy model
    for key, value in employee_update_data.dict(exclude_unset=True).items():
        setattr(update_user, key, value)
    
    db.commit()   # lưu vào DB
    db.refresh(update_user)  # cập nhật lại object nếu cần
    
    return SuccessMessageSchema(message='employee updated successfully!')