from typing import Dict, List

from logger import logger
from openai_client import OpenAIClient
from playwright_script import PlaywrightWeb

class WebAgent:

    def __init__(self, initial_url=None, questions: List[str] = None):
        self._questions: List = questions

        self._browser = PlaywrightWeb(url=initial_url, headless=False)
        self._browser.start_browser()
        self._browser.navigate_to_url()

        self._website_links: Dict = {}
        self._visited_links: Dict = {}
        self._openai_client = OpenAIClient()

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

    def choose_links(self):
        questions_str = "### Questions ####\n" + "\n".join(self._questions) + "\n########"
        links_str = "### Links ####\n" + "\n ".join([f"{text}: {url}" for url,text in self._website_links.items()]) + "\n########"
        prompt = f"""
        I'm looking for answer to following questions:
        {questions_str}
        Please choose links that may contain answers to these questions.
        {links_str}
        """

        links = self._openai_client.json_mode(prompt=prompt, response_format=List[str])

        logger.info("Chosen links: " + links)
