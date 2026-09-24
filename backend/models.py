from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's question")

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("query must not be empty or whitespace")
        return stripped


class AskResponse(BaseModel):
    answer: str
    in_scope: bool


class ErrorResponse(BaseModel):
    detail: str
