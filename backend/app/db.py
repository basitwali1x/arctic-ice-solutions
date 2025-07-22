from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    hashed_password: str

async def get_user(username: str) -> Optional[User]:
    return None  # Implement this properly
