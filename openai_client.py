import openai
from env import OPENAI_API_KEY
from logger import logger


class OpenAIClient:
    def __init__(self, model: str = None):
        # Load environment variables from .env file
        # Retrieve the API key
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set it in the .env file.")

        self._model_name: str = model
        self._client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file using OpenAI API"""

        transcript_path = audio_file_path.with_suffix('.txt')

        with open(audio_file_path, "rb") as audio_file:
            transcript = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        # Save transcript with same name as audio file
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript.text)

        logger.info(f"Saved transcript to {transcript_path.name}")
