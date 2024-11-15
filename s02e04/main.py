from enum import Enum
from pathlib import PosixPath

import download_utils
import utils
from aidevs3 import send_answer, Answer
from env import S02E04_URL_DATA
from logger import logger
from openai_client import OpenAIClient
from utils import filter_files_by_extension

SYSTEM_MESSAGE = """
Answer only with 'people,' 'robot,' or 'none.' No other responses are permitted.

It is war context. You are helping to find important information related to humans or hardware repairs.
##
Respond with 'people' if the data contains information about captured humans or if humans were spotted.
-
Respond with 'robot' if the data contains information about hardware repairs.
-
Respond with 'none' if the data does not contain any relevant information about hardware or spotted/captured humans. 
Any other information about humans or machines should be ignored - like regular activity of people or software repair/update.
"""

openai_client = OpenAIClient(model_name="gpt-4o")

DATA_DIR = './data'

transformed_data = dict()

robots = []
people = []


class ModelResponse(Enum):
    PEOPLE = "people"
    ROBOT = "robot"
    NONE = "none"


def verify_text_contains_useful_data(input: str, filename=None) -> ModelResponse:
    response: str = openai_client.ask_question(question=input, system_message=SYSTEM_MESSAGE,
                                               model_name="gpt-4o").strip().lower()

    logger.info("-----------")
    if filename:
        logger.info(f"[filename] {filename}")
    logger.info(f"[input]: {input}")
    logger.info(f"[model output]: {response}")
    logger.info("###########")

    return ModelResponse.__members__.get(response.upper(), ModelResponse.NONE)


def add_to_response(model_response: ModelResponse, filename: str):
    if model_response == ModelResponse.PEOPLE:
        people.append(filename)
    elif model_response == ModelResponse.ROBOT:
        robots.append(filename)


filepath: str = download_utils.download_file(S02E04_URL_DATA, DATA_DIR)
files: list[PosixPath] = utils.unzip_file(filepath)

text_files = filter_files_by_extension(files, ['txt'])
audio_files = filter_files_by_extension(files, ['mp3'])
image_files = filter_files_by_extension(files, ['png'])


def transform_data_and_put_in_common_structure():
    for text_file in text_files:
        text: str = utils.read_text_file(text_file)

        transformed_data[text_file.name] = text

    for audio_file in audio_files:
        transcription = openai_client.transcribe_audio(audio_file, save=False)

        transformed_data[audio_file.name] = transcription

    for image_file in image_files:
        text = openai_client.ask_with_image(image_file, question="Return text visible on the image")

        transformed_data[image_file.name] = text


def classify_all():
    for filename, text in transformed_data.items():
        response: ModelResponse = verify_text_contains_useful_data(text, filename)
        add_to_response(response, filename)


transform_data_and_put_in_common_structure()
# serialize(transformed_data)
# transformed_data = deserialize()

classify_all()

send_answer(Answer(task="kategorie", answer={
    "people": sorted(people),
    "hardware": sorted(robots)
}))
