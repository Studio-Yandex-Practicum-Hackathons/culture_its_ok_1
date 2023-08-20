from db.crud.base import CRUDBase
from models import Progress


class CRUDProgress(CRUDBase):
    pass


progress_crud = CRUDProgress(Progress)
