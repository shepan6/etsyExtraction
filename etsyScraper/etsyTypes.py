from typing import List, Optional
from pydantic import BaseModel

class EtsyShop(BaseModel):
    shop_id: int
    shop_name: str
    url: str
    review_count: int
    review_average: float
