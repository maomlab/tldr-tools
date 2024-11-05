# tldr_api.py
import argparse
import logging
from tldr_endpoint import APIManager
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def submit_module(api_manager: APIManager, module,
    receptor_pdb=None,
    actives_tgz=None, 
    decoy_tgz=None, 
    xtal_pdb=None, 
    actives_ism=None, 
    decoy_config_in=None, 
    memo=''
) -> str:
    """Submits a module and returns the job number."""
    def path_to_payload(path):
        f = open(path, "rb")
        return (None, f) 
    
    files = {}

    try:
        if module == "dockopt":
            # Open all required files for dockopt
            files['recpdb'] = path_to_payload(receptor_pdb)
            files['xtalpdb'] = path_to_payload(xtal_pdb)
            files['activestgz'] = path_to_payload(actives_tgz)
            files['decoystgz'] = path_to_payload(decoy_tgz)

        elif module == "decoys":
            files['actives.ism'] = path_to_payload(actives_ism)
            files['decoy_generation'] = path_to_payload(decoy_config_in)
        else:
            logger.error(f"Unknown module: {module}")
            return None

        # Optional fields
        if memo:
            files['memo'] = (None, memo)

        job_number = api_manager.submit_module(module, files)
        logger.info(f"Submitted Job Number: {job_number}")
        return job_number

    except Exception as e:
        logger.error(f"Error during submission: {e}")
        return None

    finally:
        # Close files after submission
        for key, value in files.items():
            if isinstance(value, tuple) and hasattr(value[1], 'close'):
                value[1].close()



def download_decoys_if_completed(api_manager: APIManager, job_number: str, output_dir: str):
    """Checks job status and downloads decoys if the job is completed."""
    try:
        if api_manager.fetch_job_status(job_number) == "Completed":
            api_manager.download_decoys(job_number, output_path=output_dir)
        else:
            logger.error(f"Job {job_number} is not completed, cannot download decoys.")
    except Exception as e:
        logger.error(f"Error checking job status or downloading decoys: {e}")

def main():
    parser = argparse.ArgumentParser(description="Submit and manage docking tasks via TLDR API.")
    parser.add_argument("--module", required=False, choices=['dockopt', 'decoys'], help="Type of module to submit.")
    parser.add_argument("--list-modules", action="store_true", help="List all available modules and exit.")

    # DUDEZ
    parser.add_argument("--activesism", required=False, help="Path to the active compounds file.")
    parser.add_argument("--decoygenin", required=False, help="Path to the active compounds file.")
    # Dockopt
    parser.add_argument("--activestgz", required=False, help="Path to the active.tgz compounds file.")
    parser.add_argument("--decoystgz", required=False, help="Path to the decoy file.")
    parser.add_argument("--xtalpdb", required=False, help="Path to the xtal file (required for dockopt).")
    parser.add_argument("--recpdb", required=False, help="Path to the receptor file (required for dockopt).")
    #Common
    parser.add_argument("--memo", default="", help="Optional memo text for the job submission.")
    parser.add_argument("--job-number", required=False, help="Job number to check status.")
    parser.add_argument("--output-dir", default="decoys", help="Directory to store downloaded decoys.")

    args = parser.parse_args()

    api_manager = APIManager()  # Initialize API manager

    if args.list_modules:
        print("Available modules:")
        for module_name, config in api_manager.module_config.items():
            print(f"- {module_name}: required fields - {config['required']}, optional fields - {config['optional']}")
        return 


    if args.job_number:
        # Check the status of the job if job number is provided
        check_job_status(api_manager, args.job_number)
    else:
        # Submit the module
        # TODO: Seperate this into a different file (config 4)
        # def submit_module(api_manager: APIManager, module: str, receptor_file: str, actives_file: str, decoy_file: str, xtal_file: str, memo: str) -> str:
        if args.module == "dockopt":
            job_number = submit_module(api_manager, args.module, 
                receptor_pdb=args.recpdb, 
                actives_tgz=args.activestgz, 
                decoy_tgz=args.decoystgz,
                xtal_pdb=args.xtalpdb, 
                memo=args.memo
            )
        elif args.module == "decoys":
            job_number = submit_module(api_manager, args.module, 
                actives_ism=args.activesism, 
                decoy_config_in=args.decoygenin, 
                memo=args.memo
            )

        # # Download the decoys if submission was successful
        # if job_number:
        #     download_decoys_if_completed(api_manager, job_number, args.output_dir)
        # else:
        #     logger.error("Failed to submit decoy generation job.")


if __name__ == "__main__":
    main()
