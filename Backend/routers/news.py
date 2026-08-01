from fastapi import APIRouterds, depends

from Backend.config.db_conf import get_db
from crud import news

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db = depends(get_db)):

    categories = await news.get_categories(db, skip=skip, limit=limit)

    return {
        "code": 200,
        "message": "Success",
        "data": categories
        }
