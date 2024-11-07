import requests
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self):
        """
        Initializes an instance of WebScraper with a state to store parsed HTML.
        """
        self._soup = None  # Internal state to store the parsed BeautifulSoup object

    def fetch_and_parse(self, url: str) -> bool:
        """
        Fetches the HTML content of the specified URL and parses it with BeautifulSoup,
        storing the result in the instance's state.

        :param url: The URL to retrieve content from.
        :return: True if the content was successfully fetched and parsed, False otherwise.
        """
        try:
            # Send an HTTP GET request to the specified URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the HTML content and store it in the instance's state
            self._soup = BeautifulSoup(response.content, 'html.parser')
            return True
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            self._soup = None
            return False

    def get_inner_text(self, selector: str, multiple: bool = False) -> str:
        """
        Retrieves the inner text of the element(s) matching the specified CSS selector,
        based on the parsed HTML stored in the instance.

        :param selector: The CSS selector to match the element(s).
        :param multiple: If True, return the text of all matched elements as a single string.
                         If False, return the text of the first matched element.
        :return: The inner text of the element(s), cleaned of excess whitespace.
        """
        if not self._soup:
            print("No content available. Please fetch and parse a page first.")
            return ""

        # Find the element(s) by selector
        if multiple:
            elements = self._soup.select(selector)
            texts = [element.get_text(strip=True) for element in elements]
            return ' '.join(texts)  # Join all texts into one string, separated by a space
        else:
            element = self._soup.select_one(selector)
            return element.get_text(strip=True) if element else ""
