import aidevs3
import download_utils
from aidevs3 import Answer
from env import S02E03_URL_DATA
from logger import logger
from openai_client import OpenAIClient

openai_client = OpenAIClient(model_name="gpt-4o")

description: str = download_utils.download_json_file_to_variable(S02E03_URL_DATA).get("description")
image_url = openai_client.generate_iamge(description)

logger.info(description)

aidevs3.send_answer(Answer(task="robotid", answer=image_url))
