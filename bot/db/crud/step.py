from db.crud.base import CRUDBase
from models import Step


class CRUDStep(CRUDBase):
    pass


step_crud = CRUDStep(Step)
