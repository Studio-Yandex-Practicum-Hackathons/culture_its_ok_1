from db.crud.base import CRUDBase
from models import Route


class CRUDRoute(CRUDBase):
    pass


route_crud = CRUDRoute(Route)
