import base64
from numbers import Number
from pathlib import Path
from typing import List

import openai
import requests
from PIL import Image
from openai import ChatCompletion
from singleton_decorator import singleton
from transformers import CLIPProcessor, CLIPModel
from openai.types.audio.transcription import Transcription
from env import OPENAI_API_KEY
from logger import logger


@singleton
class OpenAIClient:
    def __init__(self, model_name: str = "gpt-4o"):
        if not OPENAI_API_KEY:
            logger.error("OpenAI API key not found. Please set it in the .env file.")
            raise ValueError("OpenAI API key not found. Please set it in the .env file.")

        self._model_name: str = model_name
        self._client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self._clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self._clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        logger.info(f"Initialized OpenAIClient with model {self._model_name}")

    def transcribe_audio(self, audio_source: str, save: bool = True) -> str:
        """
        Transcribe audio from a local file path or URL.

        :param audio_source: Path to the local audio file or a URL.
        :param save: If True, save the transcription to a .txt file.
        :return: Transcription text.
        """
        logger.debug(f"Transcribing audio from {audio_source}")
        try:
            # Determine if the source is a URL or a local file
            if audio_source.startswith("http://") or audio_source.startswith("https://"):
                # Download the audio file
                response = requests.get(audio_source, stream=True)
                response.raise_for_status()  # Ensure the request was successful
                temp_file = Path("temp_audio_file.mp3")  # Change extension as needed
                with open(temp_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"Downloaded audio from URL: {audio_source}")
                audio_file_path = temp_file
            else:
                # Assume the source is a local file path
                audio_file_path = Path(audio_source)

            # Transcribe the audio
            with open(audio_file_path, "rb") as audio_file:
                transcript: Transcription = self._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            logger.info(f"Transcription completed for {audio_source}")

            # Save transcription if required
            if save:
                transcript_path = audio_file_path.with_suffix('.txt')
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript.text)
                logger.info(f"Saved transcript to {transcript_path.name}")

            # Clean up temporary file if downloaded
            if audio_source.startswith("http://") or audio_source.startswith("https://"):
                audio_file_path.unlink()
                logger.info(f"Deleted temporary file: {audio_file_path.name}")

            return transcript.text
        except Exception as e:
            logger.error(f"Error transcribing audio from {audio_source}: {e}", exc_info=True)
            raise

    def ask_with_image(self, image_file_path: Path, question: str, system_message: str = None) -> str:
        logger.debug(f"Asking question with image {image_file_path}")
        try:
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
                ]}
            ]

            response: ChatCompletion = self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
            )
            logger.info(f"Received response for question with image {image_file_path}")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error asking question with image {image_file_path}: {e}", exc_info=True)
            raise

    def ask_question(self, question: str, system_message: str = None, model_name: str = None) -> str:
        logger.debug(f"Asking question: {question}")
        try:
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
            logger.info(f"Received response for question: {question}")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error asking question: {question}: {e}", exc_info=True)
            raise

    def generate_image(self, prompt: str, model_name: str = "dall-e-3") -> str:
        logger.debug(f"Generating image with prompt: {prompt}")
        try:
            response = self._client.images.generate(
                model=model_name,
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="url"
            )
            image_url = response.data[0].url
            logger.info(f"Generated image URL: {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"Error generating image with prompt: {prompt}: {e}", exc_info=True)
            raise

    def embed_text(self, text):
        logger.debug(f"Embedding text: {text[:30]}...")  # Log first 30 characters
        try:
            response = self._client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            logger.info("Text embedding generated successfully.")
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error embedding text: {text[:30]}: {e}", exc_info=True)
            raise

    def embed_image(self, image_path):
        logger.debug(f"Embedding image from {image_path}")
        try:
            image = Image.open(image_path)
            inputs = self._clip_processor(images=image, return_tensors="pt", padding=True)
            embedding = self._clip_model.get_image_features(**inputs).detach().numpy().flatten()
            logger.info(f"Image embedding generated for {image_path}")
            return embedding
        except Exception as e:
            logger.error(f"Error embedding image from {image_path}: {e}", exc_info=True)
            raise

    def describe_image(self, image_source: str) -> str:
        """
        Generates a textual description of an image from a local file or URL.

        :param image_source: Path to the image file or URL.
        :return: A descriptive caption of the image.
        """
        logger.debug(f"Describing image from {image_source}")

        try:
            # Determine if the input is a URL or a local file
            if image_source.startswith("http://") or image_source.startswith("https://"):
                # Download the image
                response = requests.get(image_source)
                response.raise_for_status()
                encoded_image = base64.b64encode(response.content).decode("utf-8")
                logger.info(f"Downloaded and encoded image from URL: {image_source}")
            else:
                # Handle local file
                image_file_path = Path(image_source)
                with open(image_file_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                logger.info(f"Loaded and encoded local image: {image_file_path}")

            # Prepare messages for the API request
            messages = [
                {"role": "system", "content": "You are a helpful assistant that describes images."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the following image."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                        },
                    ],
                },
            ]

            # Call the OpenAI API
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
            )
            logger.info(f"Received response for image description from {image_source}")
            return response.choices[0].message.content

        except requests.RequestException as e:
            logger.error(f"Error downloading image from URL: {image_source}: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error describing image from {image_source}: {e}", exc_info=True)
            raise

    def embed_image_as_text(self, image_path: str) -> List[Number]:
        logger.debug(f"Embedding image as text from {image_path}")
        try:
            image_description: str = self.describe_image(image_path)
            embedding = self.embed_text(image_description)
            logger.info(f"Image embedding generated for {image_path}")
            return embedding
        except Exception as e:
            logger.error(f"Error embedding audio from {image_path}: {e}", exc_info=True)
            raise

    def embed_audio_as_text(self, audio_path) -> List[Number]:
        logger.debug(f"Embedding audio from {audio_path}")
        try:
            transcription = self._client.audio.transcriptions.create(model="whisper-1", file=audio_path)
            embedding = self.embed_text(transcription['text'])
            logger.info(f"Audio embedding generated for {audio_path}")
            return embedding
        except Exception as e:
            logger.error(f"Error embedding audio from {audio_path}: {e}", exc_info=True)
            raise
