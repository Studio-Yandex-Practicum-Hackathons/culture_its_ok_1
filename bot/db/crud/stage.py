from db.crud.base import CRUDBase
from models import Stage


class CRUDStage(CRUDBase):
    pass


stage_crud = CRUDStage(Stage)
