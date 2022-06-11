from fastapi import APIRouter
from endpoints import Index,Photos,User


router = APIRouter()
router.include_router(Index.router)
router.include_router(Photos.router)
router.include_router(User.router)