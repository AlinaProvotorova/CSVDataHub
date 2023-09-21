from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models import File


class CRUDFile(CRUDBase):

    async def get_by_filename(
            self,
            filename: str,
            session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.filename == filename
            )
        )
        return db_obj.scalars().first()


file_crud = CRUDFile(File)
