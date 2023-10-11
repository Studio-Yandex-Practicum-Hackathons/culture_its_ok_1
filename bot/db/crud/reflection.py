from datetime import datetime

from db.crud.base import CRUDBase
from models import Reflection
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDReflection(CRUDBase):
    async def get_all_by_route_stage_and_range(
            self,
            route_id: int,
            stage_id: int,
            start: datetime,
            end: datetime,
            session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.route_id == route_id,
                self.model.stage_id == stage_id,
                self.model.created_at >= start,
                self.model.created_at <= end,
            )
        )
        return db_obj.scalars().all()


reflection_crud = CRUDReflection(Reflection)
