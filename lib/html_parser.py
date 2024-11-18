from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import os
import requests
from bs4 import BeautifulSoup
from tidylib import tidy_document
from logger import logger

@dataclass
class ImageDetail:
    url: str
    name: Optional[str] = field(default=None)
    caption: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)

@dataclass
class AudioDetail:
    url: str
    name: Optional[str] = field(default=None)
    caption: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)

@dataclass
class Section:
    header: Optional[str] = field(default=None)
    content: List[str] = field(default_factory=list)
    images: List[ImageDetail] = field(default_factory=list)
    audios: List[AudioDetail] = field(default_factory=list)

@dataclass
class ParsedHtml:
    sections: List[Section]
    image_details: List[ImageDetail]
    audio_details: List[AudioDetail]


def is_valid_url(url: str) -> bool:
    """
    Validates if the given string is a well-formed URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def parse_html_from_url(url: str, user_agent: str = "Mozilla/5.0") -> ParsedHtml:
    headers = {"User-Agent": user_agent}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        raise

    soup = BeautifulSoup(response.content, 'lxml')

    sections: List[Section] = []
    image_dict: dict[str, ImageDetail] = {}  # Temporary storage for unique images
    audio_dict: dict[str, AudioDetail] = {}  # Temporary storage for unique audios

    current_section: Optional[Section] = None

    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'img', 'audio', 'figcaption', 'figure', 'a']):
        if element.name in ['h1', 'h2', 'h3']:
            # Close the current section and start a new one
            if current_section:
                sections.append(current_section)
            current_section = Section(header=element.get_text().strip())
        elif element.name == 'p' and current_section:
            # Add paragraph text to the current section
            text = element.get_text().strip()
            if text:  # Skip empty paragraphs
                current_section.content.append(text)
        elif element.name == 'figure' and current_section:
            # Process figures containing images and captions
            img = element.find('img')
            figcaption = element.find('figcaption')
            if img:
                src = img.get('src')
                if src:
                    full_url = urljoin(url, src)
                    if is_valid_url(full_url):
                        caption = figcaption.get_text().strip() if figcaption else ""
                        image_name = os.path.basename(urlparse(full_url).path)
                        image_detail = ImageDetail(url=full_url, caption=caption, name=image_name)

                        # Check if a better version exists
                        if full_url not in image_dict or len(caption) > len(image_dict[full_url].caption):
                            image_dict[full_url] = image_detail  # Replace with more detailed version

                        current_section.images.append(image_detail)
        elif element.name == 'img' and current_section:
            # Handle standalone images outside of figures
            src = element.get('src')
            if src:
                full_url = urljoin(url, src)
                if is_valid_url(full_url):
                    image_name = os.path.basename(urlparse(full_url).path)
                    image_detail = ImageDetail(url=full_url, caption="", name=image_name)

                    # Check if a better version exists
                    if full_url not in image_dict:
                        image_dict[full_url] = image_detail  # Only add if no better version exists

                    current_section.images.append(image_detail)
        elif element.name == 'audio' and current_section:
            # Handle <audio> tag with direct src attribute or <source> tags
            audio_src = element.get('src')
            if audio_src:
                full_url = urljoin(url, audio_src)
                if is_valid_url(full_url):
                    audio_name = os.path.basename(urlparse(full_url).path)
                    audio_detail = AudioDetail(url=full_url, name=audio_name, caption="")

                    # Check if a better version exists
                    if full_url not in audio_dict:
                        audio_dict[full_url] = audio_detail

                    current_section.audios.append(audio_detail)

            # Iterate through all <source> tags inside <audio>
            for source in element.find_all('source'):
                src = source.get('src')
                if src:
                    full_url = urljoin(url, src)
                    if is_valid_url(full_url):
                        audio_name = os.path.basename(urlparse(full_url).path)
                        audio_detail = AudioDetail(url=full_url, name=audio_name, caption="")

                        # Check if a better version exists
                        if full_url not in audio_dict:
                            audio_dict[full_url] = audio_detail

                        current_section.audios.append(audio_detail)
        elif element.name == 'a' and 'href' in element.attrs and current_section:
            # Handle standalone audio links
            href = element['href']
            if href.endswith(('.mp3', '.wav', '.ogg')):  # Filter audio file extensions
                full_url = urljoin(url, href)
                if is_valid_url(full_url):
                    audio_name = os.path.basename(urlparse(full_url).path)
                    audio_detail = AudioDetail(url=full_url, name=audio_name, caption=element.get_text(strip=True))

                    # Check if a better version exists
                    if full_url not in audio_dict or len(audio_detail.caption) > len(audio_dict[full_url].caption):
                        audio_dict[full_url] = audio_detail

                    current_section.audios.append(audio_detail)

    # Append the last section
    if current_section:
        sections.append(current_section)

    # Convert dictionaries to lists
    image_details = list(image_dict.values())
    audio_details = list(audio_dict.values())

    logger.info(f"Parsed {len(sections)} sections, {len(image_details)} unique images, and {len(audio_details)} unique audio files.")
    return ParsedHtml(sections=sections, image_details=image_details, audio_details=audio_details)

