"""
Anthem Blue Cross Blue Shield provider directory scraper.
"""

import logging
import time
import re
from typing import List, Dict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)

from utils.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class AnthemProviderScraper(BaseScraper):
    """
    Scraper for Anthem Blue Cross Blue Shield provider directory.
    Extracts mental health provider contact information.
    """
    
    def __init__(self, headless: bool = True) -> None:
        """Initialize the Anthem scraper with provider-specific settings."""
        self.provider_name = "anthem"
        super().__init__(headless)
        self.base_url = "https://www.anthem.com/find-care/"
        self.output_dir = f"data/{self.provider_name}"
        
    def scrape(self, zip_code: str, radius: int = 25, specialty: str = "mental_health") -> List[Dict[str, Any]]:
        """
        Scrape mental health providers from Anthem directory.
        
        Args:
            zip_code (str): ZIP code to search around
            radius (int): Search radius in miles
            specialty (str): Provider specialty to search for
        
        Returns:
            List[Dict[str, Any]]: List of provider data dictionaries
        """
        if not zip_code:
            logger.error("ZIP code is required for Anthem provider search")
            return []
            
        logger.info(f"Starting Anthem provider search for {specialty} providers in {zip_code}")
        
        try:
            # Navigate to the Anthem provider search page
            self.driver.get(self.base_url)
            
            # Select search as guest
            self._search_as_guest()
            
            # Enter location (ZIP code)
            self._enter_location(zip_code)
            
            # Select specialty
            self._select_specialty(specialty)
            
            # Set search radius
            self._set_radius(radius)
            
            # Get provider data from search results
            providers = self._extract_providers()
            
            # Save data to CSV
            self.save_data(providers, zip_code, specialty)
            
            return providers
            
        except Exception as e:
            logger.error(f"Error scraping Anthem providers: {str(e)}")
            return []
    
    def _search_as_guest(self) -> None:
        """Select the 'Search as Guest' option on the Anthem website."""
        try:
            # Wait for the page to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".homepage")))
            
            # Click on "Search as Guest" button
            guest_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search as Guest')]"))
            )
            guest_button.click()
            
            # Wait for the next page to load
            self.wait.until(EC.presence_of_element_located((By.ID, "search-location")))
            
            logger.info("Selected 'Search as Guest' option")
            
        except TimeoutException:
            logger.error("Timeout waiting for 'Search as Guest' button")
            raise
        except Exception as e:
            logger.error(f"Error selecting 'Search as Guest' option: {str(e)}")
            raise
    
    def _enter_location(self, zip_code: str) -> None:
        """
        Enter the ZIP code for provider search.
        
        Args:
            zip_code (str): ZIP code to search around
        """
        try:
            # Enter ZIP code in the location field
            location_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "search-location"))
            )
            location_input.clear()
            location_input.send_keys(zip_code)
            time.sleep(1)
            
            # Click on search/next button
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
            )
            continue_button.click()
            
            # Wait for specialty search to appear
            self.wait.until(EC.presence_of_element_located((By.ID, "search-term")))
            
            logger.info(f"Entered location: {zip_code}")
            
        except TimeoutException:
            logger.error("Timeout entering location")
            raise
        except Exception as e:
            logger.error(f"Error entering location: {str(e)}")
            raise
    
    def _select_specialty(self, specialty: str) -> None:
        """
        Select the appropriate specialty for the search.
        
        Args:
            specialty (str): Provider specialty to search for
        """
        try:
            # Map the generic specialty to Anthem-specific terms
            specialty_mapping = {
                "mental_health": "Mental Health",
                "psychiatry": "Psychiatrist",
                "psychology": "Psychologist",
                "therapy": "Therapist",
                "counseling": "Counselor"
            }
            
            search_term = specialty_mapping.get(specialty, "Mental Health")
            
            # Enter the specialty in the search box
            specialty_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "search-term"))
            )
            specialty_input.clear()
            specialty_input.send_keys(search_term)
            time.sleep(1)
            
            # Wait for suggestions to appear
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-suggestions .suggestion"))
            )
            
            # Select the first suggestion
            suggestion = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-suggestions .suggestion"))
            )
            suggestion.click()
            
            # Click on search/continue button
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search')]"))
            )
            continue_button.click()
            
            # Wait for results to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".provider-card, .no-results"))
            )
            
            logger.info(f"Selected specialty: {search_term}")
            
        except TimeoutException:
            logger.error("Timeout selecting specialty")
            raise
        except Exception as e:
            logger.error(f"Error selecting specialty: {str(e)}")
            raise
    
    def _set_radius(self, radius: int) -> None:
        """
        Set the search radius for provider search.
        
        Args:
            radius (int): Search radius in miles
        """
        try:
            # Look for radius filter
            radius_filters = self.driver.find_elements(
                By.XPATH, "//button[contains(text(), 'Distance')]"
            )
            
            if not radius_filters:
                logger.warning("Distance filter not found, using default radius")
                return
                
            # Click on radius filter button
            radius_filters[0].click()
            
            # Find the closest available radius option
            available_radius = [5, 10, 15, 25, 50, 100]
            closest_radius = min(available_radius, key=lambda x: abs(x - radius))
            
            # Select the appropriate radius option
            radius_option = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//input[@value='{closest_radius}']")
                )
            )
            radius_option.click()
            
            # Click apply button
            apply_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply')]"))
            )
            apply_button.click()
            
            # Wait for results to update
            time.sleep(2)
            
            logger.info(f"Set search radius to {closest_radius} miles")
            
        except (TimeoutException, NoSuchElementException):
            logger.warning("Could not set radius, using default")
        except Exception as e:
            logger.error(f"Error setting radius: {str(e)}")
    
    def _extract_providers(self) -> List[Dict[str, Any]]:
        """
        Extract provider information from search results.
        
        Returns:
            List[Dict[str, Any]]: List of provider data dictionaries
        """
        providers = []
        
        try:
            # Check if there are any results
            no_results = self.driver.find_elements(By.CSS_SELECTOR, ".no-results")
            if no_results:
                logger.info("No providers found matching search criteria")
                return providers
            
            # Wait for provider cards to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".provider-card"))
            )
            
            # Determine if pagination exists
            pagination = self.driver.find_elements(By.CSS_SELECTOR, ".pagination")
            has_pagination = len(pagination) > 0
            
            # If pagination exists, get the number of pages
            current_page = 1
            total_pages = 1
            
            if has_pagination:
                page_info = self.driver.find_element(By.CSS_SELECTOR, ".pagination-info").text
                page_match = re.search(r"Page (\d+) of (\d+)", page_info)
                if page_match:
                    current_page = int(page_match.group(1))
                    total_pages = int(page_match.group(2))
            
            logger.info(f"Found {total_pages} pages of results")
            
            # Process each page
            while current_page <= total_pages:
                logger.info(f"Processing page {current_page} of {total_pages}")
                
                # Wait for provider cards to load
                provider_cards = self.wait.until(
                    lambda driver: driver.find_elements(By.CSS_SELECTOR, ".provider-card")
                )
                
                # Process each provider card on the current page
                for card in provider_cards:
                    # Expand provider card to see all details
                    try:
                        expand_button = card.find_element(By.CSS_SELECTOR, ".toggle-details")
                        expand_button.click()
                        time.sleep(0.5)  # Wait for details to expand
                    except (NoSuchElementException, ElementClickInterceptedException):
                        pass  # Some cards might already be expanded
                    
                    # Extract provider data
                    provider_data = self._extract_provider_data(card)
                    if provider_data:
                        providers.append(provider_data)
                
                # Move to the next page if available
                if current_page < total_pages:
                    try:
                        next_button = self.driver.find_element(
                            By.CSS_SELECTOR, ".pagination .next"
                        )
                        next_button.click()
                        
                        # Wait for the page to load
                        self.wait.until(EC.staleness_of(provider_cards[0]))
                        time.sleep(2)
                        
                        # Wait for provider cards to load on the new page
                        self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".provider-card"))
                        )
                        
                        current_page += 1
                    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException) as e:
                        logger.error(f"Error navigating to next page: {str(e)}")
                        break
                else:
                    break
            
        except Exception as e:
            logger.error(f"Error extracting providers: {str(e)}")
        
        logger.info(f"Extracted data for {len(providers)} providers")
        return providers
    
    def _extract_provider_data(self, card) -> Dict[str, Any]:
        """
        Extract data for a single provider from the provider card.
        
        Args:
            card: Selenium WebElement for the provider card
            
        Returns:
            Dict[str, Any]: Provider data dictionary
        """
        try:
            # Initialize provider data dictionary
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
                "network": "Anthem",
                "url": self.driver.current_url
            }
            
            # Extract provider name
            name_elements = card.find_elements(By.CSS_SELECTOR, ".provider-name")
            if name_elements:
                provider_data["provider_name"] = name_elements[0].text.strip()
            
            # Extract specialty
            specialty_elements = card.find_elements(By.CSS_SELECTOR, ".specialty")
            if specialty_elements:
                provider_data["specialties"] = specialty_elements[0].text.strip()
            
            # Extract address
            address_elements = card.find_elements(By.CSS_SELECTOR, ".address")
            if address_elements:
                address_text = address_elements[0].text.strip()
                address_parts = address_text.split('\n')
                
                if len(address_parts) >= 2:
                    provider_data["address"] = address_parts[0].strip()
                    
                    # Parse city, state, zip
                    location_match = re.search(r"([^,]+),\s*(\w{2})\s*(\d{5})", address_parts[1])
                    if location_match:
                        provider_data["city"] = location_match.group(1).strip()
                        provider_data["state"] = location_match.group(2).strip()
                        provider_data["zip_code"] = location_match.group(3).strip()
            
            # Extract phone number
            phone_elements = card.find_elements(By.CSS_SELECTOR, ".phone")
            if phone_elements:
                provider_data["phone"] = phone_elements[0].text.strip()
            
            # Extract practice/facility name
            practice_elements = card.find_elements(By.CSS_SELECTOR, ".facility-name")
            if practice_elements:
                provider_data["practice_name"] = practice_elements[0].text.strip()
            
            # Extract accepting new patients status
            accepting_elements = card.find_elements(
                By.XPATH, ".//*[contains(text(), 'Accepting new patients')]"
            )
            if accepting_elements:
                status_text = accepting_elements[0].text.strip()
                provider_data["accepting_new_patients"] = "Yes" if "Yes" in status_text else "No"
            
            # Extract provider ID if available
            provider_id_elements = card.find_elements(By.CSS_SELECTOR, ".provider-id")
            if provider_id_elements:
                id_text = provider_id_elements[0].text.strip()
                id_match = re.search(r"ID:\s*(\w+)", id_text)
                if id_match:
                    provider_data["provider_id"] = id_match.group(1)
            
            return provider_data
            
        except Exception as e:
            logger.error(f"Error extracting provider data: {str(e)}")
            return None