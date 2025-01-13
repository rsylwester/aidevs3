from logger import logger
from openai_client import OpenAIClient

text_enrich_prompt = """
Analyze the following text and return only important general facts, relevant dates, and places directly related to the content. Ensure the additional information is concise and enhances understanding without repeating the original text."""

def enrich_text(text):
    openai_client = OpenAIClient(model_name="gpt-4o")
    llm_response = openai_client.ask_question(question=str(text), system_message=text_enrich_prompt, temperature=0.8)

    logger.info(f"\nEnrich text: \n>{text}\n>{llm_response}\n\n")
    return llm_response