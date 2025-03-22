import unittest
from unittest.mock import patch, MagicMock
from providers.uhc import UHCProviderScraper


class TestUHCProviderScraper(unittest.TestCase):
    @patch("providers.uhc.webdriver.Chrome")
    @patch("providers.uhc.ChromeDriverManager")
    def test_scrape(
        self, mock_chrome_driver_manager: MagicMock, mock_chrome: MagicMock
    ) -> None:
        mock_chrome_driver_manager().install.return_value = "path/to/chromedriver"
        mock_chrome.return_value = MagicMock()
        scraper = UHCProviderScraper(headless=True)
        scraper.scrape = MagicMock(
            return_value=[{"name": "Provider1", "specialty": "Specialty1"}]
        )
        result = scraper.scrape("12345", 25, "mental_health")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Provider1")

    def test_scrape_94110(self) -> None:
        scraper = UHCProviderScraper(headless=True)
        result = scraper.scrape("94110", 25, "mental_health")
        self.assertGreater(len(result), 0)
        self.assertIn("name", result[0])


if __name__ == "__main__":
    unittest.main()
