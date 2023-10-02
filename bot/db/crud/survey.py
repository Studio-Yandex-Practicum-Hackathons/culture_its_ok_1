from datetime import datetime

from db.crud.base import CRUDBase
from models import Survey
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDSurvey(CRUDBase):
    async def get_all_by_range(
            self,
            start: datetime,
            end: datetime,
            session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.created_at >= start,
                self.model.created_at <= end,
            )
        )
        return db_obj.scalars().unique().all()


survey_crud = CRUDSurvey(Survey)
