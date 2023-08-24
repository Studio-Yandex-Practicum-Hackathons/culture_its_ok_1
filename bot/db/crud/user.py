from db.crud.base import CRUDBase
from models import User


class CRUDUser(CRUDBase):
    pass


user_crud = CRUDUser(User)
