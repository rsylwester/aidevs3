from typing import Dict, List, Optional, Any, Set

from pydantic import BaseModel, Field, create_model

from lib.MarkdownConverter import MarkdownConverter
from logger import logger
from openai_client import OpenAIClient
from playwright_script import PlaywrightWeb


class WebAgent:
    class LinkLLMResponse(BaseModel):
        link: str = Field(None, description="Podaj adres mailowy do firmy SoftoAI")

    QuestionsLLMResponse = None

    @staticmethod
    def create_questions_llm_response(questions: dict):
        # Build a dict of field name -> (type, Field(...))
        fields = {}
        for key, value in questions.items():
            field_name = f"response_{key}"
            # Make the field optional with None as the default value
            fields[field_name] = (Optional[str], Field(default=None, description=value))

        # Dynamically create the model
        return create_model("QuestionsLLMResponse", **fields)

    def __init__(self, initial_url, questions: dict, md_dir: str):
        WebAgent.QuestionsLLMResponse = WebAgent.create_questions_llm_response(questions)

        self._questions: Any = WebAgent.QuestionsLLMResponse()

        self._browser = PlaywrightWeb(url=initial_url, headless=False)
        self._browser.start_browser()
        self._browser.navigate_to_url()

        self._website_links: Dict = {}
        self._visited_links: Set[str] = set()
        self._openai_client = OpenAIClient()
        self._markdown_converter = MarkdownConverter(output_dir=md_dir)

    def all_questions_answered(self):
        # Iterate over all fields in the self._questions model
        answers = {
            str(field_name).replace("response_", ""): getattr(self._questions, field_name)
            for field_name in self._questions.__fields__
        }

        return answers

    def combine_questions_objects(self, obj1, obj2):
        # Create a new instance of the same dynamic model type
        combined = self._questions.__class__()

        for field_name in self._questions.__fields__:
            # Get values from both objects
            value1 = getattr(obj1, field_name)
            value2 = getattr(obj2, field_name)

            # Set the value in the combined object
            # Prefer non-empty values from obj1, fallback to obj2
            setattr(combined, field_name, value1 or value2)

        return combined

    def links_not_visited(self):
        return {k: v for k, v in self._website_links.items() if v not in self._visited_links}

    def check_page_for_responses(self):
        mark_down_page: str = self._markdown_converter.convert_to_markdown(self._browser.url)
        questions: WebAgent.QuestionsLLMResponse = self._openai_client.json_mode(prompt=mark_down_page,
                                                                                 system_message=f"""Odpowiedz na pytania na podstawie dołączonej tresći, tylko jeśli w odpowiedzi znajduje się bezpośrednia odpowiedź na pytanie.
                                                                                 
                                                                                                Jeżeli w dołączonej treści nie ma odpowiedzi to zwróć pusty string.
                                                                                                """,
                                                                                 response_format=WebAgent.QuestionsLLMResponse)

        self._visited_links.add(self._browser.url)
        logger.info(questions)

        self._questions = self.combine_questions_objects(questions, self._questions)
        logger.info(f"Answers: {self._questions}")

        all_answers = self.all_questions_answered()
        if len([answer for answer in all_answers.values() if not answer]) == 0:
            return all_answers
        else:
            return None

    def fetch_links_as_map(self) -> Dict[str, str]:
        # Extract links and their text using JavaScript evaluation
        links = self._browser.page.eval_on_selector_all(
            "a[href]",
            """
            elements => elements
                .filter(el => el.offsetParent !== null && el.offsetHeight > 0 && el.offsetWidth > 0)  // Check visibility
                .map(el => {
                    return { text: el.innerText.trim(), href: el.href }
                })
            """
        )

        # Create a dictionary mapping link text -> URL
        links_map: dict = {link['text']: link['href'] for link in links if link['text'] and link['href']}

        logger.info(f"Links map for URL {self._browser.url}: {links_map}")

        self._website_links.update(links_map)

        return links_map

    def choose_link(self):
        not_answered_questions = [question for question in self._questions if question == '']

        questions_str = "### Questions ####\n" + "\n".join(not_answered_questions) + "\n########"
        links_str = "### Links ####\n" + "\n ".join(
            [f"{text}: {url}" for text, url in self.links_not_visited().items()]
        ) + "\n########"
        system_messsage = f"""
        I'm looking for answer to following questions:
        {questions_str}
        Please choose link that may contain answer for one of provided questions. 
        Be focus strictly on answering questions so choose links carefully.
        Do step by step analysis before choosing.
        
        RULES:
        Choose link from those provided in the prompt. Any other url is forbidden.
        """

        logger.info(f"Choosing link from not visited yet: {links_str}")
        response: WebAgent.LinkLLMResponse = self._openai_client.json_mode(prompt=links_str,
                                                                           system_message=system_messsage,
                                                                           response_format=WebAgent.LinkLLMResponse)

        logger.info(f"Chosen link:  {response.link}")
        self._browser.url = response.link
        self._browser.navigate_to_url()
