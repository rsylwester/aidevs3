import uuid
from pathlib import Path

from aidevs3 import send_answer, Answer
from download_utils import download_file
from env import OPENAI_API_KEY, S04E05_URL_NOTES
from lib.vector_db.qdrant_db import QdrantDb
from logger import logger
from openai_client import OpenAIClient
from s04e05.llm.enrich_text_with_general_facts import enrich_text
from s04e05.llm.llm_detective import answer_question, extract_answer
from s04e05.llm.text_keywords import generate_keywords_for_text
from s04e05.markdown_page_reader import MarkdownPageReader
from s04e05.pdf_extractor import PDFExtractor
from utils import is_file_exist, read_json

DATA_DIR = "data/"
NOTES_MD = Path(DATA_DIR).joinpath("notes.md").as_posix()
COLLECTION_NAME = "notes"
VECTOR_SIZE = 1536

openai_client = OpenAIClient(model_name="gpt-4o")
qdrant_db = QdrantDb()
qdrant_db.initialize_collection(collection_name=COLLECTION_NAME, vector_size=VECTOR_SIZE, recreate=False)

response: dict = {}
pdf_document = Path(DATA_DIR).joinpath("notatnik-rafala.pdf").as_posix()

if not is_file_exist(pdf_document):
    pdf_document = download_file("https://centrala.ag3nts.org/dane/notatnik-rafala.pdf", DATA_DIR)
    logger.info(pdf_document)

if not is_file_exist(NOTES_MD):
    pdf_extractor = PDFExtractor(pdf_document, OPENAI_API_KEY, DATA_DIR)
    pdf_extractor.extract()

reader = MarkdownPageReader(NOTES_MD)

# create embedings
def add_doc_embedings():
    embeddings: list = []

    try:
        while True:
            print("Create embeding for next page content:")
            pair = reader.next_pair()

            content = pair[0] + "\n\n" + pair[1]
            keywords = generate_keywords_for_text(content)
            enriched_content = f"{content}\n\n {keywords}"

            text_vector = openai_client.embed_text(enriched_content)

            embeddings.append({
                "id": str(uuid.uuid4()),
                "vector": text_vector,
                "payload": {
                    "content": content,
                }
            })

    except StopIteration:
        print("End of document.")
        qdrant_db.store_vectors(COLLECTION_NAME, embeddings)

if qdrant_db.is_collection_empty(COLLECTION_NAME):
    add_doc_embedings()

# retrieve questions to the notes

json_file = download_file(S04E05_URL_NOTES, DATA_DIR)
questions: dict = read_json(json_file)
answers: dict = {}

# fill with empty answers first
for key, question in questions.items():

    result = qdrant_db.retrieve_contexts(COLLECTION_NAME, question, top_k=3)

    context = ""
    for page_content in result:
        context += "###\n" + page_content['content'] + "###\n"

    context = context + "-----" + enrich_text(context) + "------\n"

    logger.info("######### question and answer ##############")
    print(f"Built context for question {question}: \n\n {context} \n\n")
    logger.info("--------- question and answer --------------")

    answer = answer_question(question, context)
    answers[key] = extract_answer(answer)

    logger.info(f"Short answer: {answer}")

# for key, question in questions.items():
#     if key == '01':
#         answer = openai_client.ask_question(question=str(question), system_message=SYSTEM_CONTEXT.replace("{notes_md}", read_text_file(Path(NOTES_MD))), temperature=0.8)
#         print(f"Answer: {key} - {answer}")
#         answers[key] = extract_answer(answer)


send_answer(Answer(task="notes", answer=answers))
