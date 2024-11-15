import base64
from pathlib import Path

import openai
from env import OPENAI_API_KEY
from logger import logger
from openai import ChatCompletion


class OpenAIClient:
    def __init__(self, model_name: str = "gpt-4o"):
        # Load environment variables from .env file
        # Retrieve the API key
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set it in the .env file.")

        self._model_name: str = model_name
        self._client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def transcribe_audio(self, audio_file_path: Path, save=True) -> str:
        """Transcribe audio file using OpenAI API"""

        with open(audio_file_path, "rb") as audio_file:
            transcript = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        if save:
            transcript_path = audio_file_path.with_suffix('.txt')
            # Save transcript with same name as audio file
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript.text)

            logger.info(f"Saved transcript to {transcript_path.name}")
            return transcript.text
        else:
            return transcript.text

    def ask_with_image(self, image_file_path: Path, question: str, system_message: str = None) -> str:
        """Answer a question based on an attached image using OpenAI's new API format"""

        # Encode the image in base64
        with open(image_file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        messages = [
            {"role": "system", "content": "You are a helpful assistant." if not system_message else system_message},
            {"role": "user", "content": [
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                }
            ]
             }
        ]

        response: ChatCompletion = self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
        )

        return response.choices[0].message.content

    def ask_question(self, question: str, system_message: str = None, model_name: str = None) -> str:
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": question})

        response = self._client.chat.completions.create(
            model=model_name if model_name else self._model_name,
            messages=messages,
            temperature=1.0,
            stream=False
        )

        return response.choices[0].message.content

    def generate_iamge(self, prompt: str, model_name: str = "dall-e-3") -> str:

        # Generate the image
        response = self._client.images.generate(
            model=model_name,
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )

        # Retrieve the image URL
        image_url = response.data[0].url
        logger.info(f"Generated image URL: {image_url}")

        return image_url
