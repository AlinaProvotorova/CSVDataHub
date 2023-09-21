from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


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

    async def get_multi(
            self,
            session: AsyncSession
    ):
        db_obj = await session.execute(select(self.model))
        return db_obj.scalars().all()

    async def create(
            self,
            obj_in,
            session: AsyncSession,
            user: Optional[User] = None,
            with_commit: bool = True,
    ):
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        if with_commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db_obj,
            obj_in,
            session: AsyncSession
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for filed in obj_data:
            if filed in update_data:
                setattr(db_obj, filed, update_data[filed])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
            self,
            db_obj,
            session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_not_full_objects(
            self,
            session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(self.model.fully_invested == 0
                                     ).order_by(self.model.create_date)
        )
        return db_obj.scalars().all()
