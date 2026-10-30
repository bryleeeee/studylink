import uuid

from pydantic import BaseModel, ConfigDict


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    field_of_study: str | None = None
    year_level: str | None = None
    interests: list[str] | None = None


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    display_name: str | None
    field_of_study: str | None
    year_level: str | None
    interests: list[str] | None
