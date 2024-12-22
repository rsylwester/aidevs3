import logging
import re

from playwright.sync_api import Page, Browser, Playwright
from playwright.sync_api import sync_playwright


class PlaywrightWeb:

    @property
    def url(self):
        """Getter for value."""
        return self._value

    @url.setter
    def url(self, new_value):
        """Setter for value."""
        self._value = new_value

    def __init__(self, url: str = None, headless: bool = False):

        """
        Initializes the PlaywrightScript with configuration options.

        :param url: The URL to navigate to.
        :param headless: Run in headless mode if True; otherwise, show browser UI.
        """
        self.url = url
        self.headless = headless
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.page: Page = None

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_browser(self):
        """
        Starts the Playwright browser and opens a new page.
        """
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        self.logger.info("Browser started in headless mode: %s", self.headless)

    def navigate_to_url(self):
        """
        Navigates to the specified URL.
        """
        if not self.page:
            raise ValueError("Page is not initialized. Call start_browser() first.")
        self.page.goto(self.url)
        self.logger.info("Navigated to URL: %s", self.url)

    def retrieve_and_clean_text(self, selector: str):
        """
        Retrieves text from the specified element and cleans it by removing special characters.

        :param selector: The CSS selector of the element to retrieve text from.
        :return: The cleaned text content of the element.
        """
        # Wait for the element to be available and retrieve its text content
        self.page.wait_for_selector(selector)
        text = self.page.locator(selector).inner_text()

        # Clean the text by replacing whitespace characters with a single space
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        self.logger.info(f"Original text: {text}")
        self.logger.info(f"Cleaned text: {cleaned_text}")
        return cleaned_text

    def close_browser(self):
        """
        Closes the Playwright browser and stops Playwright.
        """
        if self.browser:
            self.browser.close()
            self.logger.info("Browser closed.")
        if self.playwright:
            self.playwright.stop()
            self.logger.info("Playwright stopped.")

    def run(self):
        """
        Main method to start the browser, navigate to the URL, retrieve text, and close the browser.
        """
        try:
            self.start_browser()
            self.navigate_to_url()
            # Example: retrieve and clean text from the element with id 'human-question'
            self.retrieve_and_clean_text("#human-question")
        finally:
            self.close_browser()

    def click_element(self, selector: str, wait_for: str = None):
        """
        Clicks an element identified by the selector and waits for load completion.

        :param selector: The CSS selector for the element to click.
        :param wait_for: Optional. A CSS selector to wait for after clicking,
                         or set to 'navigation' to wait for page navigation.
        """
        # Wait for the element to be available and then click it
        self.page.wait_for_selector(selector)

        with self.page.expect_navigation() if wait_for == "navigation" else self.page.expect_load_state("load"):
            self.page.locator(selector).click()
            self.logger.info(f"Clicked element with selector: {selector}")

        # Wait for a specific element if given (for partial loads)
        if wait_for and wait_for != "navigation":
            self.page.wait_for_selector(wait_for)
            self.logger.info(f"Waited for element with selector: {wait_for} after clicking.")

    def input_text(self, selector: str, text: str):
        """
        Inputs text into a specified input field.
        :param selector: The CSS selector for the input field.
        :param text: The text to input.
        """
        self.page.wait_for_selector(selector)
        self.page.locator(selector).fill(text)
        self.logger.info(f"Input text '{text}' into element with selector: {selector}")

    def submit_form(self, form_selector: str = None, button_selector: str = None):
        """
        Submits the form either by using a form selector (direct submission)
        or by clicking a submit button.

        :param form_selector: The CSS selector for the form to submit directly.
        :param button_selector: The CSS selector for the submit button (if direct submission isn't used).
        """
        if form_selector:
            # Submit the form directly using JavaScript if form_selector is provided
            self.page.wait_for_selector(form_selector)
            self.page.evaluate(f'document.querySelector("{form_selector}").submit()')
            self.logger.info(f"Form submitted using form selector: {form_selector}")
        elif button_selector:
            # Otherwise, click the submit button
            self.page.wait_for_selector(button_selector)
            self.page.locator(button_selector).click()
            self.logger.info(f"Form submitted by clicking button with selector: {button_selector}")
        else:
            raise ValueError("Either form_selector or button_selector must be provided for form submission.")
