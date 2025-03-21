# Insurance Provider Data Extraction

A Python-based tool for extracting mental health provider contact information from insurance company directories.

## Current Targets
- UnitedHealthcare (UHC)
- Anthem Blue Cross Blue Shield

## Features
- Automated web scraping using Selenium
- Provider data extraction and organization
- Focus on mental health providers

## Requirements
- Python 3.7+
- Chrome/Firefox browser
- See requirements.txt for Python dependencies

## Setup
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install appropriate webdriver for your browser
4. Run the scraper: `python main.py`

## Project Structure
- `providers/`: Modules for each insurance provider
- `utils/`: Utility functions and helpers
- `data/`: Output directory for scraped data
- `main.py`: Entry point for running the application