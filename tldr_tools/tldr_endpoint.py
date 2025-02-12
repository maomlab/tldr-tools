import os
import requests
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TLDR_BASE_URL is defined globally
# TLDR_BASE_URL = "https://tldr.docking.org"
TLDR_BARE_URL = "tldr-dev.docking.org"
TLDR_BASE_URL = f"https://{TLDR_BARE_URL}"

class TLDREndpoints:
    """Handles endpoint management for the TLDR API."""

    @staticmethod
    def get_endpoint(endpoint: str) -> str:
        """Constructs the full URL for the specified endpoint."""
        return f"{TLDR_BASE_URL}/{endpoint}"

    @staticmethod
    def get_base_url() -> str:
        """Constructs the base URL"""
        return f"{TLDR_BASE_URL}"

def _generate_headers(cookie=None):
    """
    Generates request headers for TLDR API submission.

    Args:
    - cookie: Optional session cookie for authentication.

    Returns:
    - dict: Headers for API request.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Host': TLDR_BARE_URL,
        'Cookie': cookie,
        'Origin': TLDR_BASE_URL,
        'Referer': TLDR_BASE_URL,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    # logger.info(f"Generated headers: {headers}")
    return headers

class APIManager:
    """Manages API interactions with TLDR, including module submissions."""


    def __init__(self):
        self.api_key = self.load_api_key() 
        self.headers = _generate_headers(self.api_key)


    @staticmethod
    def load_api_key():
        """Loads the API key from the .env file."""
        load_dotenv()
        api_key = os.getenv("API_KEY") 
        if not api_key:
            raise ValueError("API_KEY not found in environment variables.")
        return api_key

    def post_request(self, url: str, files: dict) -> dict:
        """Just a generic POST request handler."""
        url_api = f"{url}?api_key={self.api_key}"

        logger.debug(f"Submitting POST REQUEST CMD: requests.post({url}, files={files}, headers={self.headers})")
        
        response = requests.post(url_api, files=files, headers=self.headers)  
        # response.raise_for_status()  
        return response  

    def _job_page_html(self, job_number):
        """
        Fetches the HTML of a job page by job number.

        Args:
        - job_number: Job number on TLDR.

        Returns:
        - str: HTML content of the job page.
        """
        job_url = f"{TLDR_BASE_URL}/results/{job_number}?api_key={self.api_key}"
        logger.info(f"Fetching results from {job_url}")

        try:
            with requests.Session() as session:
                # headers = _generate_headers(self.api_key)
                response = session.get(job_url, headers=self.headers)

                if response.status_code >= 400:
                    logger.error(f"Failed to retrieve job {job_number}, status code: {response.status_code}")
                    return None

            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching job page {job_number}: {e}")
            return None

    def fetch_job_page(self, job_number: str) -> str:
        """Fetches the HTML content of a job page by job number."""
        job_url = TLDREndpoints.get_endpoint(f"results/{job_number}?api_key={self.api_key}")
        logger.info(f"Fetching results from {job_url}")

        try:
            response = requests.get(job_url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching job page {job_number}: {e}")
            return None


    def status_by_job_no(self, job_number: str) -> str:
        """Returns the job status (Completed, Running, or Unknown) for a given job number."""
        html_content = self._job_page_html(job_number)
        return self.element_by_html(html_content, "job_status")

    def url_to_job_no(self, url: str) -> int:
        job_no = re.search(r'/(\d+)$', url)
        if job_no:
            return int(job_no.group(1))  # Return the number as an integer
        else:
            return None

    def element_by_html(self, html_content, search_id):
        #job_status or job_number
        """Returns the job status (Completed, Running, or Unknown) for a given job number."""
        if not html_content:
            return "Unknown"

        soup = BeautifulSoup(html_content, 'html.parser')
        job_status_element = soup.find('td', id='job_status')

        if job_status_element:
            return job_status_element.text.strip()
        else:
            logger.warning(f"Job status element not found.")
            return "Unknown"

    # def download_decoys(self, job_number: str, output_path="decoys"):
    #     """Downloads all decoy files for a completed job."""
    #     if self.status_by_job_no(job_number) != "Completed":
    #         raise ValueError(f"Job {job_number} is not completed.")

    #     job_url = TLDREndpoints.get_endpoint(f"results/{job_number}?api_key={self.api_key}")
    #     headers = _generate_headers(self.api_key)  
    #     response = requests.get(job_url, headers=headers)
    #     response.raise_for_status()

    #     # Assuming html on TLDR contains links to zip files
    #     zip_links = response.json().get("decoy_links", [])

    #     os.makedirs(output_path, exist_ok=True)

    #     for link in zip_links:
    #         link = f"{link}?api_key={self.api_key}"
    #         logger.info(f"Downloading link: {filename}")
    #         try:
    #             zip_response = requests.get(link, headers=headers, stream=True)
    #             zip_response.raise_for_status()
    #             filename = os.path.basename(link)
    #             with open(os.path.join(output_path, filename), 'wb') as f:
    #                 f.write(zip_response.content)
    #             logger.info(f"Downloaded decoy file: {filename}")
    #         except requests.exceptions.RequestException as e:
    #             logger.error(f"Failed to download {link}: {e}")

