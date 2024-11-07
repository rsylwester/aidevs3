from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
