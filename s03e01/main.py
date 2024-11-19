from pathlib import Path

import utils
from aidevs3 import send_answer, Answer
from logger import logger
from openai_client import OpenAIClient
from s03e01.s03e01_lib import parse_filename
from s03e01_lib import download_unzip_data
from utils import read_files_from_paths, normalize_whitespace

VECTOR_SIZE = 1536
DATA_DIR = "./data"
FACTS_DIR = "./data/facts"

IGNORE_PHRASE = "entry deleted"

PERSONALITY = """"
You are a metadata extraction expert specializing in generating rich, contextually relevant meta tags in Polish to enhance document searchability. 
Analyze the <report> text, enrich it with information from <context>, and produce rich, accurate tags in nominative form, avoiding generic terms and ensuring relevance and clarity.
"""

openai_client = OpenAIClient()

files = download_unzip_data(DATA_DIR)

txt_reports: list = utils.filter_files_by_extension(files, ["txt"])
txt_facts: list = list(Path(FACTS_DIR).iterdir())


def build_facts_context(facts: list):
    facts_context = ""
    for fact in facts:
        facts_context += f"# fact #\n{normalize_whitespace(fact)}\n#############\n"

    return facts_context


# Prepare static facts prefix
reports_data: dict = read_files_from_paths(txt_reports)
facts_data: dict = {key: value for key, value in read_files_from_paths(txt_facts).items() if
                    not value.startswith(IGNORE_PHRASE)}

facts_context = build_facts_context(list(facts_data.values()))


def build_response(report, tags_in_filename):
    prompt = f"""
    <prompt_objective>
    Generate rich, contextually accurate meta tags in Polish by analyzing the <report> text and enriching it with information from the <context> section to improve document searchability.
    </prompt_objective>
    <prompt_rules>
    Analyze the <report> and <context> texts for key nouns and noun phrases in nominative form (Polish).
    Use sysnonyms to describe data. Combine facts like: programista, specjalizuje się w pythonie -> programista python.
    Combine related facts into meaningful phrases (e.g., "programista Python," "naukowiec danych").
    Tags must be lowercase, unique, and separated by commas.
    Exclude overly generic terms unless paired with specific context.
    </prompt_rules>
    <report>[{tags_in_filename}]\n{report}</report>
    <context>{facts_context}</context>
    """
    response_tags = openai_client.ask_question(question=prompt, system_message=PERSONALITY)
    response_tags += ", " + tags_in_filename

    return response_tags


result = {}

for filename, report in reports_data.items():
    tags_in_filename: str = parse_filename(filename)
    tags = build_response(report, tags_in_filename)
    result[filename] = tags

# logger.info(f"Content from {S02E05_URL_DATA_ARTICLE} has been processed and stored!")

send_answer(Answer(task="dokumenty", answer=result))
