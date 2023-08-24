from typing import Any, Optional

from db.crud.base import CRUDBase
from models import Route
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDRoute(CRUDBase):
    async def get_all(
            self,
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort: Optional[str] = None
    ):

        db_objs = await session.execute(
            self._get_query(limit=limit, offset=offset, sort=sort)
        )
        return db_objs.scalars().unique().all()

    async def get_all_by_attribute(
            self,
            attrs: dict[str, Any],
            session: AsyncSession,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sort: Optional[str] = None
    ):
        db_objs = await session.execute(
            self._get_query(attrs=attrs, limit=limit, offset=offset, sort=sort)
        )
        return db_objs.scalars().unique().all()


route_crud = CRUDRoute(Route)
