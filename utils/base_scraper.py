"""
Base scraper module providing common functionality for provider scrapers
"""

import os
import csv
import logging
import pandas as pd
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from utils.state_license_boards import StateLicenseBoard

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Base class for insurance provider scrapers.
    Provides common functionality for web scraping and data management.
    """

    def __init__(self, headless: bool = True) -> None:
        """
        Initialize the base scraper with browser setup.

        Args:
            headless (bool): Whether to run browser in headless mode
        """
        self.provider_name = "base"
        self.output_dir = os.path.join("data", self.provider_name)
        self._setup_browser(headless)

    def _setup_browser(self, headless: bool) -> None:
        """Set up Selenium WebDriver for Chrome browser."""
        options = Options()
        if headless:
            options.add_argument("--headless")

        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")

        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
            self.wait = WebDriverWait(self.driver, 30)
            logger.info(f"Browser initialized successfully for {self.provider_name}")
        except WebDriverException as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    def close(self) -> None:
        """Close the browser and clean up resources."""
        if hasattr(self, "driver"):
            self.driver.quit()
            logger.info(f"Browser closed for {self.provider_name}")

    def save_data(
        self, providers: List[Dict[str, str]], zip_code: str, specialty: str
    ) -> None:
        """
        Save extracted provider data to CSV.

        Args:
            providers (list): List of provider dictionaries
            zip_code (str): ZIP code used for search
            specialty (str): Specialty used for search
        """
        if not providers:
            logger.warning(f"No providers found to save for {self.provider_name}")
            return

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.provider_name}_{specialty}_{zip_code}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)

        # Enrich provider data with state license board information
        providers = StateLicenseBoard.enrich_provider_data(providers)

        # Save to CSV
        df = pd.DataFrame(providers)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(providers)} providers to {filepath}")

    @abstractmethod
    def scrape(
        self, zip_code: str, radius: int = 25, specialty: str = "mental_health"
    ) -> List[Dict[str, str]]:
        """
        Abstract method to be implemented by provider-specific scrapers.

        Args:
            zip_code (str): ZIP code to search around
            radius (int): Search radius in miles
            specialty (str): Provider specialty to search for
        """
        pass
