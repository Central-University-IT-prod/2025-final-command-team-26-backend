from pydantic import BaseModel, Field


class BasicAuth(BaseModel):
    login: str = Field(
        ..., min_length=1, max_length=255, pattern=r'^[a-zA-Z0-9_.-@!]*$'
    )
    password: str = Field(..., min_length=1)
