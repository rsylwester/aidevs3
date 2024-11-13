from pathlib import Path

from logger import logger
from openai_client import OpenAIClient

openai_client = OpenAIClient(model="gpt-4o")

MAP_FILEPATH = "./data/mapa_aidevs.jpeg"

question = """
Look closely to the image with pieces of the map. They are related to one town despite the one - this one should be ignored. Please identify the name of the town basing on the details from the map. Additional hint is that town is popular bacause of spichlrzerze i twierdze. Provide chain of thoughts.
"""
answer: str = openai_client.answer_with_image(Path(MAP_FILEPATH), question=question)

logger.info(f"Model's answer: {answer}")
