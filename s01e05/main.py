from typing import Any

import requests
from aidevs3 import Answer
from env import AIDEVS_API_KEY, LLAMA2_CLOUDFLARE_API_URL, REPORT_ANSWER_URL, S01E05_URL_DATA
from logger import logger
from requests import Response

SYSTEM_MESSAGE = """
You are tasked with anonymizing personal information in a given text. Your goal is to protect individuals' privacy by replacing sensitive data with word CENZURA.

Follow these rules for anonymization:
1. Replace all first name + last name with word CENZURA.
2. Replace all street names and house number with word CENZURA.
4. Replace all dates (day, month, and year) with word CENZURA.
5. Keep all other words and punctuation unchanged.
6. Output should strictly the answer without additional prefixes or introductions (eg. Anonymized:).

##### examples #####

1)
input:

Podejrzany: Jan Kowalski mieszka przy ul. Mickiewicza 15, urodzony 05.03.1990.

output:

Podejrzany: CENZURA mieszka przy ul. CENZURA, urodzony CENZURA.

2)

input:
Osoba o imieniu i nazwisku Piotr Kowal mieszka przy ul. Maja 1, urodzony 05.03.1990, ma 20 lat.

output:
Osoba o imieniu i nazwisku CENZURA mieszka przy ul. CENZURA, urodzony CENZURA, ma CENZURA lat.

3)
Ulica - Lipowa 9 -> Ulica - CENZURA
4)
Lipowa 222 -> CENZURA
5)
Jan Kalisz -> CENZURA
6)
Osoba o imieniu Tomasz Lich. -> Osoba o imieniu CENZURA.
7)
Jan ma 22 lata -> CENZURA ma CENZURA lata 

-----

Now, please anonymize the provided text by the user and strictly follow instructions.
"""


def ask_llama(question, system_message=None):
    # Define the JSON payload with the question and optional system message
    payload = {
        "message": question,
        "system_message": system_message  # Optional system message
    }

    try:
        # Send a POST request to the API with JSON payload
        response = requests.post(LLAMA2_CLOUDFLARE_API_URL, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            return data.get("answer", "No answer found.")
        else:
            # Print error if status code is not 200
            return f"Error: {response.status_code} - {response.json().get('error', 'Unknown error')}"

    except requests.RequestException as e:
        # Handle any request exceptions
        return f"Request failed: {e}"


def send_answer(answer: Answer) -> any:
    answer_json = answer.model_dump_json(by_alias=True)
    response = requests.post(REPORT_ANSWER_URL, data=answer_json)

    logger.info(f"Sent Answer:\n: {answer_json}")

    return response.json()


def retrieve_data(url: str) -> Any:
    data: Response = requests.get(url)
    if data.status_code == 200:
        return data.text
    else:
        logger.error(f"Request failed with status code: {data.status_code}")


#### main logic

original_sentence: str = retrieve_data(S01E05_URL_DATA)
anonymized_sentence: dict = ask_llama(question=original_sentence, system_message=SYSTEM_MESSAGE).get('response')
logger.info(f"\nbefore: {original_sentence}\nafter: {anonymized_sentence}")

logger.info(f"[Sending answer]")

my_answer = Answer(task="CENZURA", apikey=AIDEVS_API_KEY, answer=anonymized_sentence)
verification_response = send_answer(my_answer)

logger.info(verification_response)
