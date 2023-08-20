from typing import Any, Callable, Optional

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_by_attribute(
            self,
            attrs: dict[str, Any],
            session: AsyncSession,
    ):
        db_obj = await session.execute(
            self._get_query(attrs=attrs)
        )
        return db_obj.scalars().first()

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
        return db_objs.scalars().all()

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
        return db_objs.scalars().all()

    async def create(
            self,
            obj_in: dict,
            session: AsyncSession,
    ):
        if not isinstance(obj_in, dict):
            raise ValueError('Объект должен иметь тип dict')

        db_obj = self.model(**obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    def _make_queries_chain(
            self,
            names: list[Any],
            values: list[Any],
            operator: Callable
    ):
        if len(names) == 1:
            return getattr(self.model, names[0]).__eq__(values[0])

        return operator(
            getattr(self.model, names[0]).__eq__(values[0]),
            self._make_queries_chain(names[1:], values[1:], operator)
        )

    def _get_query(
            self,
            *,
            attrs: dict[str, Any] | None = None,
            limit: int | None = None,
            offset: int | None = None,
            sort: str | None = None
    ):
        query = select(self.model)
        if attrs:
            query = query.where(
                self._make_queries_chain(
                    list(attrs.keys()),
                    list(attrs.values()),
                    and_
                )
            )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        if self._validate_sort_query(sort):
            query = query.order_by(text(sort))

        return query

    @staticmethod
    def _validate_sort_query(sort: Optional[str] = None) -> bool:
        if sort is None:
            return False

        field, direction = sort.split()
        if direction.lower() not in ['asc', 'desc']:
            return False

        return True
