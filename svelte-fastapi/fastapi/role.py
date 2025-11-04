from enum import Enum

class UserRole(str, Enum):
    ADMIN = 'admin'
    LEADER = 'leader'
    MEMBER = 'member'

class StatusCode(int, Enum):
    HTTP_UNAUTHORIZE_401 = 401
    HTTP_FORBIDDEN_403 = 403
    HTTP_ERROR_404 = 404
    HTTP_INTERNAL_SERVER_500 = 500