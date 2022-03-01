from typing import List, Optional
from pydantic import BaseModel

class EtsyShop(BaseModel):
    shop_id: int
    shop_name: str
    url: str
    review_count: int
    review_average: Optional[float]
    num_favorites: Optional[int]

class Review(BaseModel):
    listing_id: int
    buyer_user_id: str
    rating: Optional[int]
    review: str
    create_timestamp: int
