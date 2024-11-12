from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI


class LangchainClient:
    def __init__(self, api_key: str, model_name: str = "gpt-4o", temperature: float = 1,
                 system_message: str = "You are a helpful assistant."):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=temperature
        )
        self.system_message = SystemMessage(content=system_message)

    def ask_question(self, question: str) -> str:
        messages = [
            self.system_message,
            HumanMessage(content=question)
        ]
        response = self.llm.invoke(messages)
        return response.content
