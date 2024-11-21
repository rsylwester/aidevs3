import uuid
from datetime import datetime
from pathlib import Path

import download_utils
import utils
from aidevs3 import Answer, send_answer
from env import S03E02_URL_DATA
from lib.vector_db.qdrant_db import QdrantDb
from logger import logger
from openai_client import OpenAIClient

VECTOR_SIZE = 1536
DATA_DIR = "./data"
WEAPONS_TESTS_DIR = "./data/weapons_tests"
DOCUMENTS_DIR = "./data/weapons_tests/do-not-share"

COLLECTION_NAME = "weapons"
QUESTION = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"

openai_client = OpenAIClient()
qdrant_db = QdrantDb()


def download_and_extract_data():
    if not Path(WEAPONS_TESTS_DIR).exists():
        zip_file = download_utils.download_file(S03E02_URL_DATA, DATA_DIR)
        utils.unzip_file(zip_file, ["zip"])

    if not Path(WEAPONS_TESTS_DIR).exists():
        utils.unzip_file(Path(DATA_DIR).joinpath(Path("weapons_tests.zip")).as_posix(), extract_to=WEAPONS_TESTS_DIR,
                         password="1670")


def add_doc_embedings():
    embeddings: list = []

    for doc_file in list(Path(DOCUMENTS_DIR).iterdir()):
        document = utils.read_text_file(doc_file)
        text_vector = openai_client.embed_text(document)

        embeddings.append({
            "id": str(uuid.uuid4()),
            "vector": text_vector,
            "payload": {
                "content": document,
                "filename": doc_file.name
            }
        })

    qdrant_db.store_vectors(COLLECTION_NAME, embeddings)


def search_for_result() -> str:
    result = qdrant_db.retrieve_contexts(COLLECTION_NAME, QUESTION, top_k=1)
    logger.info(result[0]['content'])
    return result[0]['filename']


def filename_to_date(filename: str) -> str:
    """
    Transform a filename like '2024_01_29.txt' to a date in 'YYYY-MM-DD' format.

    :param filename: Filename in the format 'YYYY_MM_DD.txt'.
    :return: Date string in 'YYYY-MM-DD' format.
    :raises ValueError: If the filename does not follow the expected format.
    """
    try:
        # Extract the date part of the filename
        date_part = filename.split('.')[0]
        # Convert the extracted date part to a date object
        date_object = datetime.strptime(date_part, "%Y_%m_%d")
        # Format the date object to 'YYYY-MM-DD'
        return date_object.strftime("%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Invalid filename format: {filename}. Expected 'YYYY_MM_DD.txt'.") from e


download_and_extract_data()

qdrant_db.initialize_collection(collection_name=COLLECTION_NAME, vector_size=VECTOR_SIZE, recreate=False)

if qdrant_db.is_collection_empty(COLLECTION_NAME):
    add_doc_embedings()

filename = search_for_result()

send_answer(Answer(task="wektory", answer=filename_to_date(filename)))
