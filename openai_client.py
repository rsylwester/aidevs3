from dotenv import load_dotenv
from langchain_openai import OpenAI

from env import OPENAI_API_KEY


class OpenAIClient:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Retrieve the API key
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set it in the .env file.")

        self.llm = OpenAI(openai_api_key=OPENAI_API_KEY)

    def ask_question(self, question: str, system_message: str = None) -> str:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": question})
        return self.llm.invoke(messages)
