from env import S01E01_WEBSITE_URL, S01E01_USERNAME, S01E01_PASSWORD
from logger import logger
from openai_client import OpenAIClient
from playwright_script import PlaywrightScript
from utils import extract_human_readable_text
from web_scraper import WebScraper

openai_client = OpenAIClient()
web_scraper = WebScraper()
playwright_script = PlaywrightScript(url=S01E01_WEBSITE_URL)
playwright_script.start_browser()
playwright_script.navigate_to_url()

web_scraper.fetch_and_parse(S01E01_WEBSITE_URL)
question_text = web_scraper.get_inner_text("#human-question")

answer = openai_client.ask_question(question_text, "Answer in just number").strip()
logger.info(answer)

playwright_script.input_text('input[name="username"]', S01E01_USERNAME)
playwright_script.input_text('input[name="password"]', S01E01_PASSWORD)
playwright_script.input_text('input[name="answer"]', answer)
playwright_script.submit_form(button_selector="button#submit")

page_content = extract_human_readable_text(playwright_script.page.content())

logger.info(page_content)
