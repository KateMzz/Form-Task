from typing import Dict, Union
from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import date
from enum import Enum
import re


class FieldCategory(Enum):
    EMAIL = "email"
    DATE = "date"
    PHONE = "phone"
    TEXT = "text"


class FormValidator(BaseModel):
    fields: Dict[str, Union[date, EmailStr, str]]


class OutputValidator(BaseModel):
    categorized_fields: Dict[str, FieldCategory] = Field(default={})

    class Config:
        use_enum_values = True

    @classmethod
    def from_input_validator(cls, input_validator: FormValidator):
        categorized_fields = {
            key: cls.categorize_field(value) for key, value in input_validator.fields.items()
        }
        return cls(categorized_fields=categorized_fields)

    @staticmethod
    def categorize_field(data):
        if "@" in data and EmailStr._validate(data):
            return FieldCategory.EMAIL
        elif re.match(r"^\d{2}.\d{2}.\d{4}$", data) or re.match(r"^\d{4}-\d{2}-\d{2}$", data):
            return FieldCategory.DATE
        elif re.match(r"^\+7\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}$", data):
            return FieldCategory.PHONE
        elif isinstance(data, str):
            return FieldCategory.TEXT
