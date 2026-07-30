from fastapi import APIRouter

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories():
    return {"msg": "This endpoint will return news categories."}

