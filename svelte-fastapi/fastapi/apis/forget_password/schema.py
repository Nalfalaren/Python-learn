from pydantic import BaseModel


class RequestEmail(BaseModel):
    email: str

class ResetPasswordRequestPayload(BaseModel):
    token: str
    new_password: str
    confirm_password: str