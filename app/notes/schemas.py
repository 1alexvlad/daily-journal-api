from pydantic import BaseModel
from datetime import datetime  


class SNote(BaseModel):
    id: int
    title: str 
    content: str 
    created_at: datetime  
    updated_at: datetime  
    is_done: bool
    user_id: int

    class Config:
        from_attributes = True