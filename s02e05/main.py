import uuid
from typing import List, Tuple

import download_utils
from aidevs3 import send_answer, Answer
from env import S02E05_URL_DATA_ARTICLE, S02E05_URL_DATA_QUESTIONS
from lib.html_parser import parse_html_from_url, ParsedHtml
from lib.vector_db.qdrant_db import QdrantDb
from logger import logger
from openai_client import OpenAIClient

COLLECTION_NAME = "multimodal-embeddings"
VECTOR_SIZE = 1536  # Adjust based on embedding model dimensions
DATA_DIR = "./data"

SYSTEM_MESSAGE = """
"""

# Log the start of the download process
logger.info("Starting download of questions data.")
download_utils.download_file(S02E05_URL_DATA_QUESTIONS, DATA_DIR)
logger.info("Download completed.")

qdrant = QdrantDb(url="http://localhost:6333")
qdrant.initialize_collection(collection_name=COLLECTION_NAME, vector_size=VECTOR_SIZE, recreate=False)
logger.info(f"Initialized Qdrant collection '{COLLECTION_NAME}' with vector size {VECTOR_SIZE}.")

openai_client = OpenAIClient()


def generate_answer(query: str, contexts: List[dict], system_context="") -> str:
    """
    Generate an answer based on the given query and retrieved contexts.

    :param query: The user's query.
    :param contexts: A list of contexts retrieved from Qdrant.
    :return: The generated answer.
    """
    context_text = "\n".join(ctx['content'] for ctx in contexts)
    prompt = f"Query: {query}\n\nContext:\n{context_text}"

    return openai_client.ask_question(prompt, system_message=system_context)


def process_and_store_content(url: str):
    """
    Parses HTML content from a URL, processes its sections, and stores embeddings in Qdrant.

    :param url: The URL to fetch and parse.
    """
    logger.info(f"Processing content from URL: {url}")

    parsed_content: ParsedHtml = parse_html_from_url(url)
    logger.debug("Parsed HTML content.")

    embeddings = []

    # Process sections
    for i, section in enumerate(parsed_content.sections):
        header = section.header or ""
        combined_text = f"{header}\n{' '.join(section.content)}"

        # Initialize lists to collect image and audio info
        image_info_list: List[str] = []
        audio_info_list: List[str] = []

        # Process images in the section
        for image_detail in section.images:
            image_info = (
                f"Image:\n"
                f"------\n"
                f"Image URL: {image_detail.url}\n"
                f"------\n"
                f"Image caption: {image_detail.caption or 'No caption'}\n"
                f"------\n"
                f"Image description: {openai_client.describe_image(image_detail.url)}\n"
                f"------"
            )
            image_info_list.append(image_info)

        # Process audios in the section
        for audio_detail in section.audios:
            audio_info = (
                f"Audio:\n"
                f"------\n"
                f"Audio URL: {audio_detail.url}\n"
                f"------\n"
                f"Audio caption: {audio_detail.caption or 'No caption'}\n"
                f"------\n"
                f"Audio description: {openai_client.transcribe_audio(audio_detail.url)}\n"
                f"------"
            )
            audio_info_list.append(audio_info)

        # Combine full content description with images and audios
        full_content_description = combined_text
        if image_info_list:
            images_desc = "Images in section:\n\n" + "\n\n".join(image_info_list)
            full_content_description += "\n\n" + images_desc

        if audio_info_list:
            audios_desc = "Audios in section:\n\n" + "\n\n".join(audio_info_list)
            full_content_description += "\n\n" + audios_desc

        # Generate text embedding
        text_vector = openai_client.embed_text(full_content_description)

        embeddings.append({
            "id": str(uuid.uuid4()),
            "vector": text_vector,
            "payload": {
                "header": header,
                "content": full_content_description,
                "images": [image.__dict__ for image in section.images],  # Serialize ImageDetail objects
                "audios": [audio.__dict__ for audio in section.audios],  # Serialize AudioDetail objects
                "type": "section",
                "source": url
            }
        })

    # Store embeddings
    qdrant.store_vectors(collection_name=COLLECTION_NAME, vectors=embeddings)
    logger.info(f"Stored {len(embeddings)} embeddings in Qdrant collection '{COLLECTION_NAME}'.")


def process_questions(file_path: str, collection_name: str):
    """
    Reads questions from a file and processes each one.

    Args:
        file_path (str): Path to the file containing questions.
        collection_name (str): Name of the Qdrant collection to query.

    Returns:
        None
    """

    def parse_file(file_path: str) -> List[Tuple[str, str]]:
        """
        Reads a file with questions and parses it into a list of tuples.

        :param file_path: Path to the input file.
        :return: List of tuples with question IDs and questions.
        """
        questions: List[Tuple[str, str]] = []

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if '=' in line:
                    id, question = line.strip().split('=', 1)
                    questions.append((id, question))

        return questions

    response = {}
    # Iterate through each question
    for id, question in parse_file(file_path):
        question = question.strip()  # Remove any leading/trailing whitespace
        if not question:
            continue  # Skip empty lines

        logger.info(f"Processing Question {id}: {question}")

        # Retrieve relevant contexts from Qdrant
        contexts = qdrant.retrieve_contexts(collection_name=collection_name, query=question, top_k=2)

        # Generate an answer
        answer = generate_answer(query=question, contexts=contexts, system_context="Answer with one sentence.")

        response[id] = answer

        # Display the results
        logger.info("Answer:")
        logger.info(answer)
        logger.info("\nRelevant Contexts:")
        for ctx in contexts:
            logger.info(f"- {ctx['content']} (Score: {ctx['score']})")
        logger.info("\n" + "-" * 80 + "\n")

    return response


# File path to questions file
questions_file = "./data/arxiv.txt"

# Uncomment the next line if you need to process the article content
process_and_store_content(S02E05_URL_DATA_ARTICLE)

# Process questions
response = process_questions(file_path=questions_file, collection_name=COLLECTION_NAME)

# logger.info(f"Content from {S02E05_URL_DATA_ARTICLE} has been processed and stored!")

send_answer(Answer(task="arxiv", answer=response))
