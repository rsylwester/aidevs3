from dotenv import load_dotenv
from langchain_openai import OpenAI

from env import OPENAI_API_KEY


class OpenAIClient:
    def __init__(self, model=None):
        # Load environment variables from .env file
        load_dotenv()
        # Retrieve the API key
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set it in the .env file.")

        if model:
            self.llm = OpenAI(openai_api_key=OPENAI_API_KEY, model=model)

        self.llm = OpenAI(openai_api_key=OPENAI_API_KEY)

    def ask_question(self, question: str, system_message: str = None) -> str:
        messages = []
        if system_message:
            system_message += "Please provide a direct answer without any prefixes like 'System:'."
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": question})
        return self.llm.invoke(messages).strip()
