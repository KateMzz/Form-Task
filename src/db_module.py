from src.schemas.sch_validators import OutputValidator
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "default_database_name")
DB_COLLECTION = os.getenv("DB_COLLECTION", "default_database_name")
CLIENT = AsyncIOMotorClient(f"mongodb://mongo:27017/{DB_NAME}")


async def get_collection() -> AsyncIOMotorCollection:
    """создает и возвращает асинхронный объект коллекции MongoDB"""
    db = CLIENT[DB_NAME]
    collection = db[DB_COLLECTION]
    return collection


async def get_pipline(validator: OutputValidator) -> List[dict]:
    """Конвейер для поиска формы по заданным категориям полей"""
    match_pipeline = [
        {
            "$addFields": {
                "matchedFields": {
                    "$setIntersection": [
                        {
                            "$map": {
                                "input": {"$objectToArray": "$fields"},
                                "as": "field",
                                "in": {"$concat": ["$$field.k", ":", "$$field.v"]},
                            }
                        },
                        [f"{key}:{value}" for key, value in validator.categorized_fields.items()],
                    ]
                }
            }
        },
        {
            "$addFields": {
                "allFieldsMatched": {
                    "$eq": [
                        {"$size": "$matchedFields"},
                        {"$size": {"$objectToArray": "$fields"}},
                    ]
                }
            }
        },
        {"$match": {"allFieldsMatched": True}},
        {"$limit": 1},
        {"$project": {"name": 1}},
    ]
    return match_pipeline
