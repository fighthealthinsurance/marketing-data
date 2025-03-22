import unittest
from providers.psychology_today import PsychologyTodayScraper

class TestPsychologyTodayScraper(unittest.TestCase):
    def test_scrape(self) -> None:
        scraper = PsychologyTodayScraper(headless=True)
        result = scraper.scrape("12345", 25, "mental_health")
        self.assertGreater(len(result), 0)
        self.assertIn("name", result[0])

if __name__ == "__main__":
    unittest.main()
