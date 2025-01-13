import hashlib
import io
import os
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from logger import logger
from openai_client import OpenAIClient


class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def extract_text(self, page):
        return page.get_text()

    def extract_images(self, page):
        images = []
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = self.doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            if self.is_embedded_image(page, xref):
                images.append(image)
        return images

    def is_embedded_image(self, page, xref, size_threshold=0.90):
        """
        Determine if an image is embedded in the text by checking its size relative to the page.
        Images occupying more than `size_threshold` of the page area are considered background images.
        """
        # Get the image's bounding box
        image_rects = page.get_image_rects(xref)
        if not image_rects:
            return False  # No bounding box found

        # Assuming the image appears once on the page
        image_rect = image_rects[0]

        # Calculate the area of the image and the page
        image_area = image_rect.get_area()
        page_area = page.rect.get_area()

        # Determine if the image is smaller than the threshold
        return (image_area / page_area) < size_threshold

class ImageClassifier:
    def __init__(self, openai_api_key):
        self.openai_client = OpenAIClient(model_name="gpt-4o")

    def ask_with_image(self, question: str, system_message: str = None, image_file_path: Path = None):
        # Implement your existing method here
        pass

    def is_meaningful(self, image):
        try:
            # Save the PIL image to a temporary file
            temp_image_path = Path("temp_image.png")
            image.save(temp_image_path)
            logger.debug(f"Image saved to temporary path: {temp_image_path}")

            # Define the question and system message for GPT-4o
            question = "Does this image illustrate a real object?"
            system_message = (
                "Classify the image as 'meaningful' if it depicts a real object like: mug, house, rocks, sea, face, hand etc. "
                "or 'non-meaningful' if it shows abstract objects without real meaning like: stains, piece of plastic, liquid, lines, abstract shapes etc."
                "Response must contain word 'meaningful' or 'non-meaningful'."
                "Samples:"
                "non meaningful: stain, piece of glass, piece of plastic, some liquid, lines, circles, squares"
                "meaningful: plain, house, phone, hand, head, shoe"
            )
            logger.debug("Question and system message defined for image classification.")

            # Use the ask_with_image method to get the classification
            response = self.openai_client.ask_with_image(
                question=question,
                system_message=system_message,
                image_file_path=temp_image_path
            )
            logger.info(f"Received response from GPT-4o: {response}")

            # Interpret the response to determine if the image is meaningful
            is_meaningful = "non-meaningful" not in response.lower().strip()
            logger.debug(f"Image classified as {'meaningful' if is_meaningful else 'non-meaningful'}.")

            return is_meaningful

        except Exception as e:
            logger.error(f"An error occurred in is_meaningful: {e}")
            return False

class PDFExtractor:
    def __init__(self, pdf_path, openai_api_key, output_dir):
        self.processor = PDFProcessor(pdf_path)
        self.classifier = ImageClassifier(openai_api_key)
        self.output_dir = output_dir
        self.processed_images = set()  # Track processed image hashes
        os.makedirs(self.output_dir, exist_ok=True)


    def hash_image(self, image):
        """
        Generate a unique hash for the given image.
        """
        with io.BytesIO() as buffer:
            image.save(buffer, format="PNG")
            return hashlib.sha256(buffer.getvalue()).hexdigest()

    def extract(self):
        markdown_content = ""
        for page_num in range(self.processor.doc.page_count):
            # if page_num != 18:
            #     continue

            page = self.processor.doc.load_page(page_num)
            text = self.processor.extract_text(page)
            images = self.processor.extract_images(page)
            meaningful_images = [img for img in images if self.classifier.is_meaningful(img)]
            markdown_content += self.format_markdown(page_num, text, meaningful_images)
        return self.save_markdown(markdown_content)

    def format_markdown(self, page_num, text, images):
        md = f"## Page {page_num + 1}\n\n"
        md += text + "\n\n"

        for i, image in enumerate(images):
            # Generate a unique hash for the image
            image_hash = self.hash_image(image)

            # Skip processing if the image is already processed
            if image_hash in self.processed_images:
                continue
            self.processed_images.add(image_hash)

            # Save image and add to markdown
            image_path = os.path.join(self.output_dir, f"page_{page_num + 1}_image_{i + 1}.png")
            image.save(image_path)
            md += f"![Image {i + 1}](./{os.path.basename(image_path)})\n\n"

            # Process image text or description
            extracted_content = self.process_image(image_path)
            md += extracted_content + "\n\n"

        return md

    def process_image(self, image_path):
        """
        Process an image to either extract text or generate a detailed description.
        """
        try:
            # Extract text from the image
            question = "Extract any text present in this image. If there is no text, respond with 'no text'."
            response = self.classifier.openai_client.ask_with_image(
                question=question,
                image_file_path=Path(image_path)
            )

            if response.lower().strip() == "no text":
                # If no text, generate a detailed description
                description_question = "Describe image in concise way."
                response = self.classifier.openai_client.ask_with_image(
                    question=description_question,
                    image_file_path=Path(image_path)
                )
                return f"### Image Description\n> {response.strip()}"

            return f"### Extracted Text\n> {response.strip()}"

        except Exception as e:
            logger.error(f"An error occurred while processing the image: {e}")
            return "Error processing the image."

    def save_markdown(self, content):
        from main import NOTES_MD
        with open(NOTES_MD, "w", encoding="utf-8") as md_file:
            md_file.write(content)
