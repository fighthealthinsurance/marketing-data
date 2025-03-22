import unittest
from providers.anthem import AnthemProviderScraper

class TestAnthemProviderScraper(unittest.TestCase):
    def test_scrape(self) -> None:
        scraper = AnthemProviderScraper(headless=True)
        result = scraper.scrape("12345", 25, "mental_health")
        self.assertGreater(len(result), 0)
        self.assertIn("name", result[0])

if __name__ == "__main__":
    unittest.main()
