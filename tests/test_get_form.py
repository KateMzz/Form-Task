import httpx
import pytest
from pytest import mark


@pytest.mark.asyncio
@mark.parametrize(
    "test_input, expected_output",
    [
        (
            {
                "user_email": "vsdj@gmail.com",
                "user_phone": "+73333333333",
                "user_birthday": "2022-01-01",
                "user_gender": "Some text",
                "user": "Some text",
            },
            {"template_name": "FormUser"},
        ),
        (
            {
                "user_email": "vsdj@gmail.com",
                "user_phone": "+73333333333",
                "user_birthday": "2022-01-01",
                "usr_gender": "Some text",
            },
            {
                "user_email": "email",
                "user_phone": "phone",
                "user_birthday": "date",
                "usr_gender": "text",
            },
        ),
        (
            {
                "animal_breed": "text",
                "vaccination_date": "date",
                "animal_name": "text",
                "owner_cell": "phone",
            },
            {
                "animal_breed": "text",
                "vaccination_date": "text",
                "animal_name": "text",
                "owner_cell": "text",
            },
        ),
        (
            {
                "book_name": "Harry Potter and the Sorcerer's Stone",
                "author_name": "J.K.Rowling",
                "issued_date": "26.06.1997",
            },
            {"template_name": "BookForm"},
        ),
        ({"hello": "text", "world": "text"}, {"template_name": "NewForm2"}),
        ({}, {}),
    ],
)
async def test_get_form_successful(test_input, expected_output):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/get_form", json=test_input)
        assert response.status_code == 200
        assert response.json() == expected_output


@pytest.mark.asyncio
async def test_get_form_validation_error():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/get_form", json={"invalid_request_data": None}
        )
        assert response.status_code == 422
        assert "invalid_request_data" in response.text


@pytest.mark.asyncio
async def test_get_form_error():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/get_form")
        assert response.status_code == 422
