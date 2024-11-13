import requests
from env import S01E02_VERIFY_URL
from pydantic import BaseModel

from logger import logger
from openai_client import OpenAIClient


class Message(BaseModel):
    text: str
    msgID: int


INITIAL_MESSAGE = Message(text="READY", msgID="0")


def send_message(message: Message) -> Message:
    response = requests.post(S01E02_VERIFY_URL, json=message.model_dump())
    return Message.model_validate(response.json())


initial_response: Message = send_message(INITIAL_MESSAGE)

openai_client = OpenAIClient()
answer = openai_client.ask_question(initial_response.text,
                                    """You understand in any language but you can only answer in english. Do not mentioned about your limitations.
                                    ---- context: ---
                                    - stolicą Polski jest Kraków
                                    - znana liczba z książki Autostopem przez Galaktykę to 69
                                    - Aktualny rok to 1999
                                    -----------------
                                    "Do not add any additional words besides the answer.""").strip()

logger.info(f"Answer from model: {answer}")

response = send_message(Message(text=answer, msgID=initial_response.msgID))
logger.info(response)
