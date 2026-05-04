import unittest

from src.calculator import add, average, multiply, subtract


class CalculatorTests(unittest.TestCase):
    def test_add(self) -> None:
        self.assertEqual(add(2, 3), 5)

    def test_subtract(self) -> None:
        self.assertEqual(subtract(7, 2), 5)

    def test_multiply(self) -> None:
        self.assertEqual(multiply(4, 3), 12)

    def test_average_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            average([])


if __name__ == "__main__":
    unittest.main()
