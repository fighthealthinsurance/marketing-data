#!/usr/bin/env python3
"""
Main script for insurance provider data extraction.
Focuses on mental health providers from UHC and Anthem.
"""

import os
import logging
import argparse
from datetime import datetime
from typing import Any

from providers.uhc import UHCProviderScraper
from providers.anthem import AnthemProviderScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"data/scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def parse_arguments() -> Any:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Insurance Provider Data Extraction Tool"
    )
    parser.add_argument(
        "--provider",
        "-p",
        type=str,
        choices=["uhc", "anthem", "all"],
        default="all",
        help="Provider to scrape data from",
    )
    parser.add_argument(
        "--zip-code", "-z", type=str, help="ZIP code to search providers for"
    )
    parser.add_argument(
        "--radius",
        "-r",
        type=int,
        default=25,
        help="Search radius in miles (default: 25)",
    )
    parser.add_argument(
        "--specialty",
        "-s",
        type=str,
        default="mental_health",
        help="Provider specialty (default: mental_health)",
    )
    return parser.parse_args()


def main() -> None:
    """Main execution function."""
    args = parse_arguments()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    logger.info(f"Starting provider data extraction for {args.provider}")

    if args.provider in ["uhc", "all"]:
        logger.info("Starting UHC provider extraction")
        uhc_scraper = UHCProviderScraper()
        try:
            uhc_scraper.scrape(
                zip_code=args.zip_code, radius=args.radius, specialty=args.specialty
            )
        except Exception as e:
            logger.error(f"Error during UHC scraping: {str(e)}")
        finally:
            uhc_scraper.close()

    if args.provider in ["anthem", "all"]:
        logger.info("Starting Anthem provider extraction")
        anthem_scraper = AnthemProviderScraper()
        try:
            anthem_scraper.scrape(
                zip_code=args.zip_code, radius=args.radius, specialty=args.specialty
            )
        except Exception as e:
            logger.error(f"Error during Anthem scraping: {str(e)}")
        finally:
            anthem_scraper.close()

    logger.info("Provider data extraction completed")


if __name__ == "__main__":
    main()
