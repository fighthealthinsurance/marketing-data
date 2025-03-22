"""
UnitedHealthcare (UHC) provider directory scraper.
"""

import logging
import time
from typing import List, Dict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

from utils.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class UHCProviderScraper(BaseScraper):
    """
    Scraper for UnitedHealthcare (UHC) provider directory.
    Extracts mental health provider contact information.
    """

    def __init__(self, headless: bool = True) -> None:
        """Initialize the UHC scraper with provider-specific settings."""
        self.provider_name = "uhc"
        super().__init__(headless)
        self.base_url = "https://www.uhc.com/find-a-doctor"
        self.output_dir = f"data/{self.provider_name}"

    def scrape(
        self, zip_code: str, radius: int = 25, specialty: str = "mental_health"
    ) -> List[Dict[str, Any]]:
        """
        Scrape mental health providers from UHC directory.

        Args:
            zip_code (str): ZIP code to search around
            radius (int): Search radius in miles
            specialty (str): Provider specialty to search for

        Returns:
            List[Dict[str, Any]]: List of provider data dictionaries
        """
        if not zip_code:
            logger.error("ZIP code is required for UHC provider search")
            return []

        logger.info(
            f"Starting UHC provider search for {specialty} providers in {zip_code}"
        )

        try:
            # Navigate to the UHC provider search page
            self.driver.get(self.base_url)

            # Select search as guest
            self._search_as_guest()

            # Select behavioral health directory
            self._select_behavioral_health_directory()

            # Select employer and individual plans
            self._select_employer_individual_plans()

            # Select specialty
            self._select_specialty(specialty)

            # Enter location and search radius
            self._enter_location(zip_code, radius)

            # Get provider data from search results
            providers = self._extract_providers()

            # Save data to CSV
            self.save_data(providers, zip_code, specialty)

            return providers

        except Exception as e:
            logger.error(f"Error scraping UHC providers: {str(e)}")
            return []

    def _search_as_guest(self) -> None:
        """Select the 'Search as Guest' option on the UHC website."""
        try:
            guest_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Search as a guest')]")
                )
            )
            guest_button.click()
            self.wait.until(EC.presence_of_element_located((By.ID, "search-location")))
            logger.info("Selected 'Search as Guest' option")
        except TimeoutException:
            logger.error("Timeout waiting for 'Search as Guest' button")
            raise
        except Exception as e:
            logger.error(f"Error selecting 'Search as Guest' option: {str(e)}")
            raise

    def _select_behavioral_health_directory(self) -> None:
        """Select the 'Behavioral Health Directory' option on the UHC website."""
        try:
            behavioral_health_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(), 'Behavioral Health Directory')]")
                )
            )
            behavioral_health_button.click()
            self.wait.until(EC.presence_of_element_located((By.ID, "search-location")))
            logger.info("Selected 'Behavioral Health Directory' option")
        except TimeoutException:
            logger.error("Timeout waiting for 'Behavioral Health Directory' button")
            raise
        except Exception as e:
            logger.error(
                f"Error selecting 'Behavioral Health Directory' option: {str(e)}"
            )
            raise

    def _select_employer_individual_plans(self) -> None:
        """Select the 'Employer and Individual Plans' option on the UHC website."""
        try:
            plans_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(), 'Employer and Individual Plans')]")
                )
            )
            plans_button.click()
            self.wait.until(EC.presence_of_element_located((By.ID, "search-location")))
            logger.info("Selected 'Employer and Individual Plans' option")
        except TimeoutException:
            logger.error("Timeout waiting for 'Employer and Individual Plans' button")
            raise
        except Exception as e:
            logger.error(
                f"Error selecting 'Employer and Individual Plans' option: {str(e)}"
            )
            raise

    def _select_specialty(self, specialty: str) -> None:
        """
        Select the appropriate specialty in the search form.

        Args:
            specialty (str): Provider specialty to search for
        """
        try:
            specialty_mapping = {
                "mental_health": "Therapist",
                "psychiatry": "Psychiatrist",
                "psychology": "Psychologist",
                "therapy": "Therapist",
            }
            search_term = specialty_mapping.get(specialty, "Therapist")
            specialty_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "search-term"))
            )
            specialty_input.clear()
            specialty_input.send_keys(search_term)
            time.sleep(1)
            specialty_input.send_keys(Keys.DOWN)
            specialty_input.send_keys(Keys.ENTER)
            logger.info(f"Selected specialty: {search_term}")
        except TimeoutException:
            logger.error("Timeout while selecting specialty")
            raise
        except Exception as e:
            logger.error(f"Error selecting specialty: {str(e)}")
            raise

    def _enter_location(self, zip_code: str, radius: int) -> None:
        """
        Enter location information and search radius.

        Args:
            zip_code (str): ZIP code to search around
            radius (int): Search radius in miles
        """
        try:
            location_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "search-location"))
            )
            location_input.clear()
            location_input.send_keys(zip_code)
            time.sleep(1)
            location_input.send_keys(Keys.ENTER)
            try:
                radius_select = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "search-radius"))
                )
                available_radius = [5, 10, 15, 25, 50, 100]
                closest_radius = min(available_radius, key=lambda x: abs(x - radius))
                radius_select.click()
                radius_option = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//option[@value='{closest_radius}']")
                    )
                )
                radius_option.click()
                logger.info(f"Selected search radius: {closest_radius} miles")
            except (TimeoutException, NoSuchElementException):
                logger.warning("Could not set radius, using default")
            search_button = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@type='submit' and contains(text(), 'Search')]",
                    )
                )
            )
            search_button.click()
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".provider-info, .no-results-message")
                )
            )
        except TimeoutException:
            logger.error("Timeout while entering location")
            raise
        except Exception as e:
            logger.error(f"Error entering location: {str(e)}")
            raise

    def _extract_providers(self) -> List[Dict[str, Any]]:
        """
        Extract provider information from search results.

        Returns:
            List[Dict[str, Any]]: List of provider data dictionaries
        """
        providers: List[Dict[str, Any]] = []
        try:
            no_results = self.driver.find_elements(
                By.CSS_SELECTOR, ".no-results-message"
            )
            if no_results:
                logger.info("No providers found matching search criteria")
                return providers
            total_pages = 1
            pagination = self.driver.find_elements(
                By.CSS_SELECTOR, ".pagination-container"
            )
            if pagination:
                page_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, ".pagination-container li"
                )
                if page_elements and len(page_elements) > 2:
                    try:
                        total_pages = int(page_elements[-2].text)
                    except ValueError:
                        total_pages = 1
            logger.info(f"Found {total_pages} pages of results")
            current_page = 1
            while current_page <= total_pages:
                logger.info(f"Processing page {current_page} of {total_pages}")
                provider_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, ".provider-info"
                )
                for element in provider_elements:
                    provider_data = self._extract_provider_data(element)
                    if provider_data:
                        providers.append(provider_data)
                if current_page < total_pages:
                    try:
                        next_button = self.driver.find_element(
                            By.CSS_SELECTOR, ".pagination-container li:last-child a"
                        )
                        next_button.click()
                        time.sleep(2)
                        self.wait.until(EC.staleness_of(provider_elements[0]))
                        self.wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".provider-info")
                            )
                        )
                    except (
                        NoSuchElementException,
                        ElementClickInterceptedException,
                        TimeoutException,
                    ) as e:
                        logger.error(f"Error navigating to next page: {str(e)}")
                        break
                current_page += 1
        except Exception as e:
            logger.error(f"Error extracting providers: {str(e)}")
        logger.info(f"Extracted data for {len(providers)} providers")
        return providers

    def _extract_provider_data(self, provider_element: Any) -> Dict[str, Any]:
        """
        Extract data for a single provider from the provider element.

        Args:
            provider_element: Selenium WebElement for the provider

        Returns:
            Dict[str, Any]: Provider data dictionary
        """
        try:
            provider_data = {
                "provider_id": "",
                "provider_name": "",
                "practice_name": "",
                "specialties": "",
                "address": "",
                "city": "",
                "state": "",
                "zip_code": "",
                "phone": "",
                "accepting_new_patients": "",
                "network": "UHC",
                "url": self.driver.current_url,
            }
            name_element = provider_element.find_elements(By.CSS_SELECTOR, "h2")
            if name_element:
                provider_data["provider_name"] = name_element[0].text.strip()
            address_elements = provider_element.find_elements(
                By.CSS_SELECTOR, ".address-container .address"
            )
            if address_elements:
                full_address = address_elements[0].text.strip()
                address_parts = full_address.split("\n")
                if len(address_parts) >= 2:
                    provider_data["address"] = address_parts[0].strip()
                    location_parts = address_parts[1].split(",")
                    if len(location_parts) >= 2:
                        provider_data["city"] = location_parts[0].strip()
                        state_zip = location_parts[1].strip().split(" ")
                        if len(state_zip) >= 2:
                            provider_data["state"] = state_zip[0].strip()
                            provider_data["zip_code"] = state_zip[1].strip()
            phone_elements = provider_element.find_elements(
                By.CSS_SELECTOR, ".phone-number"
            )
            if phone_elements:
                provider_data["phone"] = phone_elements[0].text.strip()
            practice_elements = provider_element.find_elements(
                By.CSS_SELECTOR, ".facility-name"
            )
            if practice_elements:
                provider_data["practice_name"] = practice_elements[0].text.strip()
            specialty_elements = provider_element.find_elements(
                By.CSS_SELECTOR, ".specialty-list"
            )
            if specialty_elements:
                provider_data["specialties"] = specialty_elements[0].text.strip()
            accepting_elements = provider_element.find_elements(
                By.XPATH, ".//*[contains(text(), 'Accepting new patients:')]"
            )
            if accepting_elements:
                status_text = accepting_elements[0].text.strip()
                provider_data["accepting_new_patients"] = (
                    "Yes" if "Yes" in status_text else "No"
                )
            return provider_data
        except Exception as e:
            logger.error(f"Error extracting provider data: {str(e)}")
            return {}
