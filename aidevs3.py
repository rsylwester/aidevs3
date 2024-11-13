from typing import Any

import requests
from env import REPORT_ANSWER_URL, AIDEVS_API_KEY
from logger import logger
from pydantic import BaseModel
from pydantic import Field


class Answer(BaseModel):
    task: str
    apikey: str = Field(default=AIDEVS_API_KEY)
    answer: Any


def send_answer(answer: Answer) -> any:
    answer_json = answer.model_dump_json(by_alias=True)
    response = requests.post(REPORT_ANSWER_URL, data=answer_json)

    logger.info(f"Sent answer in json:\n: {answer_json}")

    response_json = response.json()

    logger.info(f"Received response in json:\n: {response_json}")
