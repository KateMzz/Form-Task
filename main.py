from typing import Union, Dict
from pydantic_core import ValidationError
from fastapi import FastAPI, HTTPException, Depends
from src.schemas.sch_validators import FormValidator, OutputValidator
from motor.motor_asyncio import AsyncIOMotorCollection
from src.log_conf import logger
from src.services import populate_forms, retrieve_form
from src.db_module import get_collection

app = FastAPI()


@app.post("/get_form")
async def get_form(
    validator: FormValidator = Depends(FormValidator),
    collection: AsyncIOMotorCollection = Depends(get_collection),
) -> Union[str, Dict]:
    """
     Асинхронно обрабатывает запрос на получение шаблона формы по валидированным данным.

    :param validator: Валидированные данные формы.
    :param collection: Коллекция MongoDB.
    :return: Строка с именем найденного шаблона или словарь с категориями полей.
    """
    try:
        await populate_forms(collection)
        output_validator = OutputValidator.from_input_validator(validator)
        logger.info(f"getting template name")
        template = await retrieve_form(output_validator, collection)
        return template
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
