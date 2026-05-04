import unittest

from src.report_formatter import render_report


class ReportFormatterTests(unittest.TestCase):
    def test_render_report_includes_title_and_summary(self) -> None:
        result = render_report("Daily Report", "Summary line", [])
        self.assertIn("# Daily Report", result)
        self.assertIn("Summary line", result)

    def test_render_report_filters_blank_items(self) -> None:
        result = render_report("Daily Report", "Summary line", ["first", " ", "second"])
        self.assertIn("- first", result)
        self.assertIn("- second", result)
        self.assertNotIn("-  ", result)


if __name__ == "__main__":
    unittest.main()
