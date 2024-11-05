import argparse
import logging
import os
from dotenv import load_dotenv
from tldr_endpoint import *  
from bs4 import BeautifulSoup
import requests

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_decoys(api_manager: APIManager, job_number: str, output_path: str):
    """Downloads all decoy files for a completed job."""
    html_content = api_manager.fetch_job_page(job_number)

    if not html_content:
        logger.error("Failed to fetch job details; cannot download decoys.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    # decoy_links = soup.find_all('a', class_='decoy_link')  # Assuming class for decoy links
    decoy_links = soup.find_all('a', download=True)

    if not decoy_links:
        logger.warning("No decoy links found for the specified job.")
        return

    os.makedirs(output_path, exist_ok=True)

    for link in decoy_links:
        decoy_url = f"{TLDREndpoints.get_base_url()}{link['href']}"  
        filename = os.path.basename(decoy_url)
        
        try:
            response = requests.get(decoy_url)
            response.raise_for_status() 
            
            with open(os.path.join(output_path, filename), 'wb') as f:
                f.write(response.content)
            logger.info(f"Downloaded decoy file: {filename}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {decoy_url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download decoys from TLDR API based on job number.")
    parser.add_argument("--job-number", required=True, help="Job number to download decoys for.")
    parser.add_argument("--output", default="decoys", help="Directory to save downloaded decoys.")
    args = parser.parse_args()

    api_manager = APIManager()  
    download_decoys(api_manager, args.job_number, args.output)

if __name__ == "__main__":
    main()
