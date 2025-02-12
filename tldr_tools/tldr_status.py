import argparse
import logging
from tldr_tools.tldr_endpoint import APIManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_job_status(api_manager: APIManager, job_number: str):
    """Fetches and logs the status of a job."""
    status = api_manager.status_by_job_no(job_number)
    logger.info(f"Job Number: {job_number}, Status: {status}")
    return status

def main():
    # Command-line interface for checking job status
    parser = argparse.ArgumentParser(description="Check the status of a job via TLDR API.")
    parser.add_argument("--job-number", required=True, help="Job number to check status.")
    args = parser.parse_args()

    api_manager = APIManager() 
    check_job_status(api_manager, args.job_number)


if __name__ == "__main__":
    main()