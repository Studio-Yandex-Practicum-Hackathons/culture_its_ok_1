from db.crud.base import CRUDBase
from models import Object


class CRUDObject(CRUDBase):
    pass


object_crud = CRUDObject(Object)
