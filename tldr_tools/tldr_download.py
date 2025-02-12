import argparse
import logging
import os
from dotenv import load_dotenv
from tldr_tools.tldr_endpoint import *  
from bs4 import BeautifulSoup
import requests
import time

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for retry behavior
MAX_RETRIES = 5  # Number of retries before giving up
RETRY_DELAY = 5  # Time in seconds between retries

def download_decoys(api_manager, job_number: str, output_path: str, retries: int = MAX_RETRIES):
    """Downloads all decoy files for a completed job with retry logic."""
    html_content = api_manager.fetch_job_page(job_number)

    if not html_content:
        logger.error("Failed to fetch job details; cannot download results.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    decoy_links = soup.find_all('a', download=True)  # Assuming decoy links are in 'a' tags with 'download' attribute

    if not decoy_links:
        logger.warning("No decoy links found for the specified job.")
        return

    os.makedirs(output_path, exist_ok=True)

    for link in decoy_links:
        decoy_url = f"{TLDREndpoints.get_base_url()}{link['href']}?api_key={api_manager.api_key}"
        logger.info(f"Downloading: {decoy_url}")
        filename = os.path.basename(link['href'])

        # Retry logic for downloading each decoy file
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"Attempt {attempt} to download decoy file: {filename}")
                response = requests.get(decoy_url, headers=api_manager.headers)
                response.raise_for_status()

                with open(os.path.join(output_path, filename), 'wb') as f:
                    f.write(response.content)
                logger.info(f"Downloaded decoy file: {filename}")
                break  # Exit the retry loop if download is successful

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download {decoy_url}: {e}")

                if attempt == retries:
                    logger.error(f"Max retries reached for {decoy_url}. Giving up.")
                    return False
                else:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)

    return True

def main():
    parser = argparse.ArgumentParser(description="Download decoys from TLDR API based on job number.")
    parser.add_argument("--job-number", required=True, help="Job number to download decoys for.")
    parser.add_argument("--output", default="decoys", help="Directory to save downloaded decoys.")
    args = parser.parse_args()

    api_manager = APIManager()  
    download_decoys(api_manager, args.job_number, args.output)

if __name__ == "__main__":
    main()
