import unittest
from unittest.mock import patch, MagicMock
from providers.psychology_today import PsychologyTodayScraper

class TestPsychologyTodayScraper(unittest.TestCase):
    @patch('providers.psychology_today.webdriver.Chrome')
    @patch('providers.psychology_today.ChromeDriverManager')
    def test_scrape(self, mock_chrome_driver_manager, mock_chrome):
        mock_chrome_driver_manager().install.return_value = 'path/to/chromedriver'
        mock_chrome.return_value = MagicMock()
        scraper = PsychologyTodayScraper(headless=True)
        scraper.scrape = MagicMock(return_value=[{'name': 'Provider1', 'specialty': 'Specialty1'}])
        result = scraper.scrape('12345', 25, 'mental_health')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Provider1')

if __name__ == '__main__':
    unittest.main()
