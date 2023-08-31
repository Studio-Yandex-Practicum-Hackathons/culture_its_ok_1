from datetime import datetime

from db.crud.base import CRUDBase
from models import Progress
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDProgress(CRUDBase):
    async def get_usage_count(
            self,
            user_id: int,
            session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.user_id == user_id
            )
        )
        return len(db_obj.scalars().all())

    async def get_all_by_route_and_date_range(
            self,
            route_id: int,
            start: datetime,
            end: datetime,
            session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.route_id == route_id,
                self.model.started_at >= start,
                self.model.started_at <= end,
            )
        )
        return db_obj.scalars().all()


progress_crud = CRUDProgress(Progress)
