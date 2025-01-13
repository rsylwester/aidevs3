import re

class MarkdownPageReader:
    def __init__(self, filepath):
        """
        Initialize the MarkdownPageReader with a file path.
        """
        self.filepath = filepath
        self.pages = []
        self.current_pair_start = -1  # Start before the first pair
        self._load_file()

    def _load_file(self):
        """
        Load and parse the Markdown file into pages.
        """
        with open(self.filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        # Split content into pages based on "## Page" markers
        raw_pages = content.split("## Page")[1:]
        # Remove page numbers from the start of each page and clean up
        self.pages = [self._strip_page_number(page.strip()) for page in raw_pages]

    @staticmethod
    def _strip_page_number(page_content):
        """
        Remove the page number at the start of the content, if it exists.
        """
        # Remove leading numbers and spaces (e.g., "1\n" or "2 ")
        return re.sub(r'^\d+\s*\n*', '', page_content)

    def next_pair(self):
        """
        Move to the next pair of pages and return their content.
        """
        if self.current_pair_start < len(self.pages) - 2:
            self.current_pair_start += 1
            return self.pages[self.current_pair_start], self.pages[self.current_pair_start + 1]
        else:
            raise StopIteration("No more pairs of pages.")

    def prev_pair(self):
        """
        Move to the previous pair of pages and return their content.
        """
        if self.current_pair_start > 0:
            self.current_pair_start -= 1
            return self.pages[self.current_pair_start], self.pages[self.current_pair_start + 1]
        else:
            raise StopIteration("No previous pairs of pages.")

    def reset(self):
        """
        Reset the reader to the beginning.
        """
        self.current_pair_start = -1

    def get_total_pages(self):
        """
        Get the total number of pages.
        """
        return len(self.pages)

    def get_total_pairs(self):
        """
        Get the total number of pairs of pages.
        """
        return max(0, len(self.pages) - 1)