from enum import Enum
from typing import List

from pydantic import BaseModel

from aidevs3 import send_answer, Answer
from logger import logger
from openai_client import OpenAIClient
from s04e01.config import SMALL_IMAGE_SUFFIX
from utils import add_suffix

openai_client = OpenAIClient()


class ImageAction(Enum):
    REPAIR = "REPAIR"
    DARKEN = "DARKEN"
    BRIGHTEN = "BRIGHTEN"

    DONE = "DONE"

    @classmethod
    def improve_image_commands(cls):
        return [cls.REPAIR, cls.BRIGHTEN, cls.DARKEN]

    @classmethod
    def done_command(cls):
        return cls.DONE


class ImageAnalysisResult(BaseModel):
    action: ImageAction
    reason: str


class Images(BaseModel):
    image_urls: List[str]

    class Config:
        title = "Images"


class BooleanResponse(BaseModel):
    result: bool


# Function to communicate with the API
def communicate_with_api(answer):
    logger.info("Sending answer to API: %s", answer)
    response = send_answer(Answer(task="photos", answer=answer))
    logger.info(f"Response from api: {response}")

    return response


def issue_command(command, file_name):
    response = communicate_with_api(f"{command} {file_name}")
    return response


def start_conversation():
    logger.info("Sending START command to API.")
    response = communicate_with_api("START")
    logger.info("Received response from API: %s", response)
    return response


def extract_iamges(message: str, small: bool = False) -> List[str]:
    response = openai_client.json_mode(prompt=message,
                                       system_message="Create a list with information image filename -> image url ",
                                       response_format=Images)
    image_urls = []

    if small:
        for image_url in response.image_urls:
            image_urls.append(add_suffix(image_url, SMALL_IMAGE_SUFFIX))
    else:
        image_urls = response.image_urls

    logger.info(f"Image urls: {image_urls}")
    return image_urls
