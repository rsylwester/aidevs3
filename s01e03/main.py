from typing import List, Optional, Any

import requests
from env import AIDEVS_API_KEY
from logger import logger
from openai_client import OpenAIClient
from pydantic import BaseModel, Field
from requests import Response


class Answer(BaseModel):
    task: str
    apikey: str
    answer: Any


class Test(BaseModel):
    q: str
    a: str


class TestData(BaseModel):
    question: str
    answer: int
    test: Optional[Test] = None


class CalibrationData(BaseModel):
    apikey: str = Field(..., alias='apikey')
    description: str
    copyright: str
    test_data: List[TestData] = Field(..., alias='test-data')


URL = f"https://centrala.ag3nts.org/data/{AIDEVS_API_KEY}/json.txt"
ANSWER_URL = f"https://centrala.ag3nts.org/report"

openai_client = OpenAIClient()


def send_answer(answer: Answer) -> any:
    answer_json = answer.model_dump_json(by_alias=True)
    response = requests.post(ANSWER_URL, data=answer_json)

    logger.info(f"Sent Answer:\n: {answer_json}")

    return response.json()


def retrieve_data(url: str) -> CalibrationData:
    data: Response = requests.get(url)

    # Check if the request was successful
    if data.status_code == 200:
        json_data = data.json()
        return CalibrationData(**json_data)
    else:
        print(f"Request failed with status code: {data.status_code}")


def fix_calibration_data(calibration_data: CalibrationData):
    for test_data in calibration_data.test_data:

        result = eval(test_data.question)
        test_data.answer = result

        if test_data.test:
            ai_answer = openai_client.ask_question(test_data.test.q)
            test_data.test.a = ai_answer
            logger.info(f"----\nQ: {test_data.test.q}\n A: {test_data.test.a}\n----")

    calibration_data.apikey = AIDEVS_API_KEY


calibration_data: CalibrationData = retrieve_data(URL)
fix_calibration_data(calibration_data)

logger.info(f"[Sending answer]")

my_answer = Answer(task="JSON", apikey=AIDEVS_API_KEY, answer=calibration_data)
verification_response = send_answer(my_answer)

logger.info(verification_response)
