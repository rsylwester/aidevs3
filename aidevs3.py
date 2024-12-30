from dataclasses import dataclass
from typing import Any
import httpx
import requests
from env import REPORT_ANSWER_URL, AIDEVS_API_KEY
from logger import logger
from pydantic import BaseModel
from pydantic import Field


class Answer(BaseModel):
    task: str
    apikey: str = Field(default=AIDEVS_API_KEY)
    answer: Any


@dataclass
class Response:
    code: int
    message: str


def send_answer(answer: Answer) -> Response:
    answer_json = answer.model_dump_json(by_alias=True)
    response = requests.post(REPORT_ANSWER_URL, data=answer_json)

    logger.info(f"Sent answer in json:\n: {answer_json}")

    response_json = response.json()
    api_response = Response(code=response_json.get("code"), message=response_json.get("message"))

    logger.info(f"Received response in json:\n: {response_json}")

    return api_response


async def send_answer_async(answer: Answer) -> Response:
    answer_json = answer.model_dump_json(by_alias=True)
    async with httpx.AsyncClient() as client:

        timeout = httpx.Timeout(connect=60.0, read=60.0, write=60.0, pool=60.0)
        response = await client.post(REPORT_ANSWER_URL, data=answer_json, timeout=timeout)
        logger.info(f"Sent answer with async in json:\n: {answer_json}")

        response_json = response.json()

        logger.info(f"Received response in json:\n: {response_json}")

        api_response = Response(code=response_json.get("code"), message=response_json.get("message"))
        return api_response
