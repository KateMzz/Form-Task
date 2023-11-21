import pytest
from pydantic import ValidationError
from pytest import mark

from src.schemas.sch_validators import FormValidator, FieldCategory, OutputValidator


@pytest.mark.asyncio
async def test_validate_data():
    data = {
        "email": "test@example.com",
        "date": "2023-11-16",
        "phone": "+7 123 456 78 90",
        "text": "Some text",
    }
    form_validator = FormValidator(fields=data)
    assert form_validator


@pytest.mark.asyncio
async def test_invalidate_data():
    data = {
        "email": "test@example.com",
        "date": "2023-11-16",
        "phone": "+7 123 456 78 90",
        "text": None,
        "another_text": False,
    }

    with pytest.raises(ValidationError):
        FormValidator(fields=data)


@pytest.mark.asyncio
@mark.parametrize(
    "test_input, expected_category",
    [
        ({"email": "test@example.com"}, FieldCategory.EMAIL),
        ({"date": "2023-11-16"}, FieldCategory.DATE),
        ({"phone": "+7 123 456 78 90"}, FieldCategory.PHONE),
        ({"text": "some text"}, FieldCategory.TEXT),
        ({"wrong_email": "testexample.com"}, FieldCategory.TEXT),
        ({"wrong_date": "2023/11/16"}, FieldCategory.TEXT),
        ({"wrong_phone": "+7 123 456 78 900"}, FieldCategory.TEXT),
        ({"empty_text": ""}, FieldCategory.TEXT),
    ],
)
async def test_categorize_field(test_input, expected_category):
    result = OutputValidator.categorize_field(list(test_input.values())[0])
    assert result == expected_category
