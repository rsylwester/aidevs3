import requests
import html2text
from urllib.parse import urlparse, urljoin
import os

class MarkdownConverter:
    def __init__(self, output_dir="pages_md"):
        self.output_dir = output_dir
        # Ensure the output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def file_exists(self, filename):
        """Check if the file already exists in the output directory."""
        file_path = os.path.join(self.output_dir, filename)
        return os.path.exists(file_path)

    def url_to_filename(self, url):
        """Generate a filename based on the URL."""
        parsed_url = urlparse(url)
        filename = parsed_url.path.split("/")[-1] or "index"  # Default to 'index' if path ends with /
        if not filename.endswith(".md"):
            filename += ".md"  # Ensure the file has a .md extension
        return filename

    def convert_to_markdown(self, url):
        """Fetch the website content and save it as a markdown file."""
        try:
            # Generate the output filename
            filename = self.url_to_filename(url)

            # Check if the file already exists
            file_path = os.path.join(self.output_dir, filename)

            if self.file_exists(filename):
                print(f"File already exists: {file_path}")
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                return content

            # Fetch the website content
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for HTTP errors

            # Extract base URL
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

            # Convert HTML to Markdown
            html_content = response.text
            markdown_converter = html2text.HTML2Text()
            markdown_converter.ignore_links = False  # Keep links in markdown
            markdown_converter.inline_links = True  # Use inline links for images and other resources

            # Prepend base URL to image paths
            markdown_converter.images_to_base_url = base_url
            markdown_content = markdown_converter.handle(html_content)

            # Replace relative image URLs with full URLs
            markdown_content = self._convert_image_urls(markdown_content, base_url)

            # Save to file
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(markdown_content)
            print(f"Markdown saved to {file_path}")

            return markdown_content

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
        except Exception as e:
            print(f"Error converting HTML to Markdown: {e}")

    def _convert_image_urls(self, markdown_content, base_url):
        """Replace relative image URLs with absolute URLs."""
        lines = markdown_content.splitlines()
        updated_lines = []
        for line in lines:
            if line.strip().startswith("!["):  # Markdown image syntax
                # Example: ![alt text](relative_path)
                start_idx = line.find("(")
                end_idx = line.find(")", start_idx)
                if start_idx != -1 and end_idx != -1:
                    relative_url = line[start_idx + 1 : end_idx]
                    full_url = urljoin(base_url, relative_url)
                    line = line[:start_idx + 1] + full_url + line[end_idx:]
            updated_lines.append(line)
        return "\n".join(updated_lines)

