from datetime import datetime

from db.crud.base import CRUDBase
from models import Progress
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDProgress(CRUDBase):
    async def get_date_range(
        self, session: AsyncSession, id: int, start: datetime, end: datetime
    ):
        db_obj = await session.execute(
            select(Progress).where(
                Progress.route_id == id,
                Progress.started_at >= start,
                Progress.started_at <= end,
            )
        )
        return db_obj.scalars().all()


progress_crud = CRUDProgress(Progress)
