from pydantic import BaseModel, field_validator
from datetime import datetime  


class SNote(BaseModel):
    id: int
    title: str 
    content: str 
    created_at: datetime  
    updated_at: datetime  
    is_done: bool
    user_id: int

    @field_validator('id')
    def check_id_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ID не может быть отрицательным")
        return value

    class Config:
        from_attributes = True