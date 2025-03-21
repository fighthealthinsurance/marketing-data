import unittest
from unittest.mock import patch, MagicMock
from utils.base_scraper import BaseScraper


class TestBaseScraper(unittest.TestCase):
    @patch("utils.base_scraper.webdriver.Chrome")
    @patch("utils.base_scraper.ChromeDriverManager")
    def test_setup_browser(
        self, mock_chrome_driver_manager: MagicMock, mock_chrome: MagicMock
    ) -> None:
        mock_chrome_driver_manager().install.return_value = "path/to/chromedriver"
        mock_chrome.return_value = MagicMock()
        scraper = BaseScraper(headless=True)
        scraper._setup_browser(headless=True)
        self.assertIsNotNone(scraper.driver)
        self.assertIsNotNone(scraper.wait)

    @patch("utils.base_scraper.pd.DataFrame.to_csv")
    @patch("utils.base_scraper.os.makedirs")
    def test_save_data(self, mock_makedirs: MagicMock, mock_to_csv: MagicMock) -> None:
        scraper = BaseScraper(headless=True)
        providers = [{"name": "Provider1", "specialty": "Specialty1"}]
        scraper.save_data(providers, "12345", "mental_health")
        mock_makedirs.assert_called_once()
        mock_to_csv.assert_called_once()

    @patch("utils.base_scraper.webdriver.Chrome")
    @patch("utils.base_scraper.ChromeDriverManager")
    def test_close(
        self, mock_chrome_driver_manager: MagicMock, mock_chrome: MagicMock
    ) -> None:
        mock_chrome_driver_manager().install.return_value = "path/to/chromedriver"
        mock_chrome.return_value = MagicMock()
        scraper = BaseScraper(headless=True)
        scraper.close()
        scraper.driver.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
