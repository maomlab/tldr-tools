import os
import requests
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TLDR_BASE_URL is defined globally
TLDR_BASE_URL = "https://tldr.docking.org"

class TLDREndpoints:
    """Handles endpoint management for the TLDR API."""
    
    @staticmethod
    def load_api_key():
        """Loads the API key from the .env file."""
        load_dotenv()
        api_key = os.getenv("API_KEY") 
        if not api_key:
            raise ValueError("API_KEY not found in environment variables.")
        return api_key

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'tldr.docking.org',
        'Cookie': cookie,
        'Origin': TLDR_BASE_URL,
        'Referer': TLDR_BASE_URL,
        'Upgrade-Insecure-Requests': '1'
    }
    # logger.info(f"Generated headers: {headers}")
    return headers

class APIManager:
    """Manages API interactions with TLDR, including module submissions."""

    def get_available_modules(self):
        """Return a list of available modules for submission."""
        return self.modules
    
    def __init__(self):
        self.api_key = TLDREndpoints.load_api_key() 


        # TODO: Seperate this into a different file (config 1)
        self.module_config = {
            "dockopt": {
                "required": ["actives.tgz", "decoys.tgz", "rec.pdb", "xtal-lig.pdb"],
                "optional": ["memo"]
            },
            "decoys": {
                "required": ["actives.ism", "decoy_generation"],
                "optional": ["memo"]
            }
        }

        self.modules = self.module_config.keys()

    def submit_module(self, module: str, data: dict) -> str:
        """Submits a module based on the module type and data."""
        self.validate_input(module, data)  # Validate input before submission

        logger.debug(f"Submitting {module} job with data:\n{data}")

        if module == "dockopt":
            return self._submit_dockopt(data)
        elif module == "decoys":
            return self._submit_decoys(data)
        else:
            raise ValueError(f"Unknown module: {module}")

    def validate_input(self, module: str, data: dict):
        """Validates the input data based on required and optional fields."""
        config = self.module_config.get(module)

        if not config:
            raise ValueError(f"Module {module} is not configured.")

        # Check required fields
        for field in config["required"]:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")


    # TODO: Seperate this into a different file (config 2)
    def _submit_dockopt(self, data: dict) -> str:
        """Handles Dockopt submission."""
        url = TLDREndpoints.get_endpoint(f"submit/dockopt?api_key={self.api_key}")
        response = self.post_request(url, data)
        return response.get('job_number')

    def _submit_decoys(self, data: dict) -> str:
        """Handles decoy gen (called DUDEZ on TLDR) submission."""
        #	https://tldr.docking.org/submit/dudez
        url = TLDREndpoints.get_endpoint(f"submit/dudez?api_key={self.api_key}") 
        response = self.post_request(url, data)
        return response.get('job_number')

    def post_request(self, url: str, data: dict) -> dict:
        """Just a generic POST request handler."""
        headers = _generate_headers()  
        logger.info(f"Submitting POST REQUEST CMD: requests.post({url}, files={data}, headers={headers})")
        
        response = requests.post(url, files=data, headers=headers)  
        response.raise_for_status()  
        return response.json()  

    def _job_page_html(self, job_number):
        """
        Fetches the HTML of a job page by job number.

        Args:
        - job_number: Job number on TLDR.

        Returns:
        - str: HTML content of the job page.
        """
        job_url = f"{TLDR_BASE_URL}results/{job_number}?api_key={self.api_key}"
        logger.info(f"Fetching results from {job_url}")

        try:
            with requests.Session() as session:
                headers = _generate_headers()
                response = session.get(job_url, headers=headers)

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


    def fetch_job_status(self, job_number: str) -> str:
        """Returns the job status (Completed, Running, or Unknown) for a given job number."""
        html_content = self._job_page_html(job_number)

        if not html_content:
            return "Unknown"

        soup = BeautifulSoup(html_content, 'html.parser')
        job_status_element = soup.find('td', id='job_status')

        if job_status_element:
            return job_status_element.text.strip()
        else:
            logger.warning(f"Job status element not found for job {job_number}")
            return "Unknown"

    def download_decoys(self, job_number: str, output_path="decoys"):
        """Downloads all decoy files for a completed job."""
        if self.fetch_job_status(job_number) != "Completed":
            raise ValueError(f"Job {job_number} is not completed.")

        job_url = TLDREndpoints.get_endpoint(f"results/{job_number}?api_key={self.api_key}")
        headers = _generate_headers()  
        response = requests.get(job_url, headers=headers)
        response.raise_for_status()

        # Assuming html on TLDR contains links to zip files
        zip_links = response.json().get("decoy_links", [])

        os.makedirs(output_path, exist_ok=True)

        for link in zip_links:
            try:
                zip_response = requests.get(link)
                zip_response.raise_for_status()
                filename = os.path.basename(link)
                with open(os.path.join(output_path, filename), 'wb') as f:
                    f.write(zip_response.content)
                logger.info(f"Downloaded decoy file: {filename}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download {link}: {e}")

