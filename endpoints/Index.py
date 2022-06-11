from fastapi import APIRouter


#APIRouter creates path operations for user module
router = APIRouter(
    tags=["Home"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", tags=["Home"], summary="Home", description="Home", response_description="Home")
def home():
    return {"message": "Hello World"}
