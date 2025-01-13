import os

import fitz
from markitdown import MarkItDown
from openai import OpenAI

from env import OPENAI_API_KEY
import pymupdf4llm


def convert_file_to_markdown_with_pymupdf4llm(source_path: str, target_path: str):
    md_text = pymupdf4llm.to_markdown(source_path, write_images=True, pages=[0], page_chunks=True, extract_words=True)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    with open(target_path, 'w', encoding='utf-8') as file:
        file.write(md_text)

        print(f"Markdown content saved to {target_path}")

def convert_file_to_markdown_with_markitdown(source_path: str, target_path: str):
    client = OpenAI(api_key=OPENAI_API_KEY)
    md = MarkItDown(llm_client=client, llm_model="gpt-4o")
    md_result = md.convert(source_path)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    with open(target_path, 'w', encoding='utf-8') as file:
        file.write(md_result.text_content)

        print(f"Markdown content saved to {target_path}")

def extract_images_without_background(pdf_path, output_folder):
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Check if the image is a background image
            # Background images often have large dimensions covering the entire page
            # Adjust the threshold dimensions as needed
            if base_image["width"] > 1000 and base_image["height"] > 1000:
                continue  # Skip background images

            # Save the image
            image_ext = base_image["ext"]
            image_filename = f"{output_folder}/page_{page_num + 1}_image_{img_index + 1}.{image_ext}"
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)
