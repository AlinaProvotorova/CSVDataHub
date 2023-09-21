from fastapi import APIRouter

from app.api.endpoints import file_router, user_router

main_router = APIRouter()

main_router.include_router(
    file_router,
    prefix='/file',
    tags=['File']
)
main_router.include_router(user_router)
