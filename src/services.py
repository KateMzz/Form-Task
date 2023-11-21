from typing import Dict, List, Any, Optional

from pydantic_core import ValidationError
from fastapi import HTTPException
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError, OperationFailure
import aiofiles


from src.schemas.sch_validators import OutputValidator
from motor.motor_asyncio import AsyncIOMotorCollection
import json
from .log_conf import logger
from src.db_module import get_pipline
from cachetools import TTLCache


FILE_NAME = "form_templates.json"
CACHE = TTLCache(maxsize=2000, ttl=2000)


async def read_form_templates(file_name: str) -> List[Dict[str, Any]]:
    """Асинхронно читает содержимое файла с шаблонами форм и возвращает список словарей."""
    async with aiofiles.open(file_name, "r") as file:
        contents = await file.read()
    return json.loads(contents)


async def get_existing_document(
    collection: AsyncIOMotorCollection, form_name: str
) -> Optional[Dict[str, Any]]:
    """Асинхронно получает существующий документ из коллекции или кэша по имени формы."""
    return CACHE.get(form_name) or await collection.find_one({"name": form_name})


async def update_cache_and_build_operation(
    collection: AsyncIOMotorCollection,
    form_name: str,
    form_template: Dict[str, Any],
    insert_operations: List[UpdateOne],
) -> None:
    """"Асинхронно обновляет кеш, строит операцию вставки в коллекцию и добавляет ее в список операций."""
    existing_document = await get_existing_document(collection, form_name)
    CACHE[form_name] = existing_document

    if not existing_document:
        insert_operations.append(
            UpdateOne(
                filter={"name": form_name},
                update={"$set": {"fields": form_template["fields"]}},
                upsert=True,
            )
        )


async def populate_forms(collection: AsyncIOMotorCollection) -> None:
"""Асинхронно заполняет коллекцию формами, считанными из файла шаблонов."""
    try:
        form_templates = await read_form_templates(FILE_NAME)
        insert_operations = []

        for form_template in form_templates:
            form_name = form_template["name"]
            await update_cache_and_build_operation(
                collection, form_name, form_template, insert_operations
            )

        if insert_operations:
            result = await collection.bulk_write(insert_operations)
            logger.info(f"I've added {result.upserted_count} new forms to the collection")
    except (FileNotFoundError, IOError, BulkWriteError, OperationFailure, KeyError) as e:
        logger.error(f"There was an error with the file: {e}")


async def retrieve_form(
    validator: OutputValidator, collection: AsyncIOMotorCollection
) -> str | Dict:
"""Асинхронно возвращает шаблон формы, соответствующий переданным валидированным данным или словарь с полями и типом данных"""
    try:
        match_pipeline = await get_pipline(validator)
        template = await collection.aggregate(match_pipeline).next()
        if template:
            template_name = template.get("name")
            return {"template_name": template_name}
        return validator.categorized_fields

    except StopAsyncIteration:
        return validator.categorized_fields
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
