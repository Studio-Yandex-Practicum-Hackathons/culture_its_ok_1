from db.crud.base import CRUDBase
from models import Reflection


class CRUDReflection(CRUDBase):
    pass


reflection_crud = CRUDReflection(Reflection)
