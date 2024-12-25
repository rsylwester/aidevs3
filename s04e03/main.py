from pathlib import Path

from aidevs3 import send_answer, Answer
from logger import logger

import download_utils
from env import S04E03_URL_DATA, S04E03_URL_WEBSITE
from tools.tools import WebAgent
from utils import get_filename_from_url, read_json, is_file_exist

DATA_DIR = './data'
MD_DIR = Path(DATA_DIR).joinpath("md_dir")
questions_file: Path = Path(DATA_DIR, get_filename_from_url(S04E03_URL_DATA))


if not is_file_exist(str(questions_file)):
    download_utils.download_file(S04E03_URL_DATA, DATA_DIR)

questions = read_json(questions_file)

web_agent = WebAgent(S04E03_URL_WEBSITE, questions=questions, md_dir=str(MD_DIR))

answers = None

for i in range(20):

    answers = web_agent.check_page_for_responses()
    if answers:
        logger.info(f"All answers {answers}")
        break
    web_agent.fetch_links_as_map()
    web_agent.choose_link()

send_answer(Answer(task="softo", answer=answers))
