import re
import string
import unittest

from s04e04.main import split_instruction, transform_instruction_to_coordinates_move, get_terrain


class TestMain(unittest.TestCase):

    def normalize_string(self, text):
        """
        Normalize a string by:
        - Removing punctuation
        - Removing filler words ('i', 'a') only at the start and end
        - Stripping extra whitespace
        - Converting to lowercase for consistent comparison
        """
        # Remove punctuation
        text = re.sub(rf"[{re.escape(string.punctuation)}]", "", text)

        # Split into words
        words = text.split()

        # Define filler words to remove
        fillers = {"i", "a"}

        # Remove fillers at the start
        while words and words[0].lower() in fillers:
            words.pop(0)

        # Remove fillers at the end
        while words and words[-1].lower() in fillers:
            words.pop()

        # Join words back into a string and return in lowercase
        return " ".join(words).strip().lower()

    def test_split_instruction(self):
        instruction = "Poleciałem jedno pole w prawo, a później na sam dół i na koniec jeden w prawo."
        expected = [
            "Poleciałem jedno pole w prawo",
            "a później na sam dół",
            "i na koniec jeden w prawo",
        ]

        # Call the function to test
        result = split_instruction(instruction)

        # Normalize both expected and result before comparison
        normalized_expected = [self.normalize_string(e) for e in expected]
        normalized_result = [self.normalize_string(r) for r in result]

        # Check if each normalized expected string is included in the corresponding normalized result
        for expected_part, result_part in zip(normalized_expected, normalized_result):
            with self.subTest(expected=expected_part, result=result_part):
                self.assertTrue(
                    expected_part in result_part or result_part in expected_part,
                    f"Expected part '{expected_part}' not found in result part '{result_part}'."
                )

    def test_transform_instruction_to_coordinates_move__right_move(self):
        instruction = "poleciałem jedno pole w prawo"
        expected = [1, 0]  # Replace with the actual expected coordinates
        result = transform_instruction_to_coordinates_move(instruction)
        self.assertEqual(result, expected)

    def test_transform_instruction_to_coordinates_move__bottom_move(self):
        instruction = "a później na sam dół"
        expected = [0, 3]  # Replace with the actual expected coordinates
        result = transform_instruction_to_coordinates_move(instruction)
        self.assertEqual(result, expected)

    def test_get_terrain_basic_move(self):
        # Test a basic movement
        moves = [[1, 0], [0, 1]]  # Move down, then right
        result = get_terrain(moves)
        self.assertEqual(result, "wiatrak")

    def test_get_terrain_basic_move_right_down_twice(self):
        # Test a basic movement
        moves = [[2, 0], [0, 3]]  # Move down, then right
        result = get_terrain(moves)
        self.assertEqual(result, "samochód")

    def test_get_terrain_basic_move_twice_down(self):
        # Test a basic movement
        moves = [[0, 1], [0, 2]]  # Move down, then right
        result = get_terrain(moves)
        self.assertEqual("skały", result)


if __name__ == '__main__':
    unittest.main()
