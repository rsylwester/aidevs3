from logger import logger
from openai_client import OpenAIClient

question_enrich_prompt = """
You are an AI assistant designed to extract keywords for better search and retrieval. For every input question, identify the main subject and relevant terms.

Rules:
1. Focus on brevity and relevance.
2. Include the main subject, specific names, locations, dates, or entities.
3. Add synonyms or related terms where helpful.

Return the result in this format:

Question: <original question>
Keywords: <keyword1>, <keyword2>, <keyword3>, ...

Examples:

Input:
Do którego roku przeniósł się Rafał?

Output:
Question: Do którego roku przeniósł się Rafał?
Keywords: Rafał, rok, przeniesienie, podróż w czasie

Input:
Kto wpadł na pomysł, aby Rafał przeniósł się w czasie?

Output:
Question: Kto wpadł na pomysł, aby Rafał przeniósł się w czasie?
Keywords: pomysł, Rafał, inicjator, podróż w czasie
"""

def enrich_question(question):
    openai_client = OpenAIClient(model_name="gpt-4o")
    llm_response = openai_client.ask_question(question=str(question), system_message=question_enrich_prompt, temperature=0.8)

    logger.info(f"\nEnrich question: \n>{question}\n>{llm_response}\n\n")

    return llm_response