import logging
import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException
)
from utils.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class PsychologyTodayScraper(BaseScraper):
    """
    Scraper for Psychology Today provider directory.
    Extracts mental health provider contact information.
    """
    
    def __init__(self, headless: bool = True) -> None:
        """Initialize the Psychology Today scraper with provider-specific settings."""
        self.provider_name = "psychology_today"
        super().__init__(headless)
        self.base_url = "https://www.psychologytoday.com/us/therapists"
        self.output_dir = f"data/{self.provider_name}"
        
    def scrape(self, zip_code: str, radius: int = 25, specialty: str = "mental_health") -> List[Dict[str, Any]]:
        """
        Scrape mental health providers from Psychology Today directory.
        
        Args:
            zip_code (str): ZIP code to search around
            radius (int): Search radius in miles
            specialty (str): Provider specialty to search for
        
        Returns:
            List[Dict[str, Any]]: List of provider data dictionaries
        """
        if not zip_code:
            logger.error("ZIP code is required for Psychology Today provider search")
            return []
            
        logger.info(f"Starting Psychology Today provider search for {specialty} providers in {zip_code}")
        
        try:
            # Navigate to the Psychology Today provider search page
            self.driver.get(self.base_url)
            
            # Enter location (ZIP code)
            self._enter_location(zip_code)
            
            # Select specialty
            self._select_specialty(specialty)
            
            # Get provider data from search results
            providers = self._extract_providers()
            
            # Save data to CSV
            self.save_data(providers, zip_code, specialty)
            
            return providers
            
        except Exception as e:
            logger.error(f"Error scraping Psychology Today providers: {str(e)}")
            return []
    
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
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Search')]"))
            )
            continue_button.click()
            
            # Wait for results to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".results")))
            
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
            # Map the generic specialty to Psychology Today-specific terms
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
                EC.presence_of_element_located((By.CSS_SELECTOR, ".results"))
            )
            
            logger.info(f"Selected specialty: {search_term}")
            
        except TimeoutException:
            logger.error("Timeout selecting specialty")
            raise
        except Exception as e:
            logger.error(f"Error selecting specialty: {str(e)}")
            raise
    
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
            
            # Process each provider card
            provider_cards = self.driver.find_elements(By.CSS_SELECTOR, ".provider-card")
            for card in provider_cards:
                # Extract provider data
                provider_data = self._extract_provider_data(card)
                if provider_data:
                    providers.append(provider_data)
            
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
                "network": "Psychology Today",
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
