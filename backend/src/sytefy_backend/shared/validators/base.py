"""Shared Pydantic utilities."""

from typing import Any

from pydantic import BaseModel, model_validator


class StrictModel(BaseModel):
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }

    @model_validator(mode="before")
    @classmethod
    def strip_strings(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                key: value.strip() if isinstance(value, str) else value
                for key, value in data.items()
            }
        if isinstance(data, str):
            return data.strip()
        return data
