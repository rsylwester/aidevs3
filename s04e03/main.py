from pathlib import Path

import download_utils
from aidevs3 import send_answer, Answer
from env import S04E03_URL_DATA, S04E03_URL_WEBSITE
from openai_client import OpenAIClient
from s04e03.tools.tools import WebAgent
from utils import get_filename_from_url, read_text_file, read_json

DATA_DIR = './data'
questions_file = Path(DATA_DIR, get_filename_from_url(S04E03_URL_DATA))



if not questions_file:
    download_utils.download_file(S04E03_URL_DATA, DATA_DIR)

questions = read_json(questions_file)
web_agent = WebAgent(S04E03_URL_WEBSITE, questions.values())

openai_client = OpenAIClient()

web_agent.fetch_links_as_map()
web_agent.choose_links()

# send_answer(Answer(task="softo", answer=None))
