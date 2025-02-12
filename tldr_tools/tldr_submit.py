# tldr_api.py
import argparse
import logging
from tldr_tools.tldr_endpoint import *
from tldr_tools.tldr_status import check_job_status
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODULE_CONFIG = {
    "dockopt": {
        "endpoint": "submit/dockopt",
        "description": "Optimization pipeline for DOCK38",
        "required_files": {
            "recpdb": "recpdb",
            "xtalpdb": "xtalpdb",
            "activestgz": "activestgz",
            "decoystgz": "decoystgz",
        },
        "optional": ["memo"],
        "cli_args": [
            {"name": "--activestgz", "help": "Path to actives.tgz file.", "required": True},
            {"name": "--decoystgz", "help": "Path to decoys.tgz file.", "required": True},
            {"name": "--recpdb", "help": "Path to receptor PDB file.", "required": True},
            {"name": "--xtalpdb", "help": "Path to xtal ligand PDB file.", "required": True},
            {"name": "--memo", "help": "Optional memo text.", "required": False},
        ],
    },
    "build": {
        "endpoint": "submit/build3d38",
        "description": "Prepare a 3D library for docking in up to four formats used by popular docking programs using DOCK3.8 pipeline.",
        "required_files": {
            "input": "input.txt",
        },
        "optional": ["memo"],
        "cli_args": [
            {"name": "--input", "help": "File of SMILES ([SMILES] [COMPOUND_NAME] per line).", "required": True},
            {"name": "--memo", "help": "Optional memo text.", "required": False},
        ],
    },
    "decoys": {
        "endpoint": "submit/dudez",
        "description": "Decoy generation module for active compound generation.",
        "required_files": {
            "activesism": "actives.ism",
            "decoygenin": "decoy_generation",
        },
        "optional": ["memo"],
        "cli_args": [
            {"name": "--activesism", "help": "Path to active.ism file.", "required": True},
            {"name": "--decoygenin", "help": "Path to decoy_generation.in file.", "required": True},
            {"name": "--memo", "help": "Optional memo text.", "required": False},
        ],
    },
}


def download_decoys_if_completed(api_manager: APIManager, job_number: str, output_dir: str):
    """Checks job status and downloads decoys if the job is completed."""
    try:
        if api_manager.status_by_job_no(job_number) == "Completed":
            api_manager.download_decoys(job_number, output_path=output_dir)
        else:
            logger.error(f"Job {job_number} is not completed, cannot download decoys.")
    except Exception as e:
        logger.error(f"Error checking job status or downloading decoys: {e}")

def add_module_arguments(parser, module_name, module_config):
    """Adds CLI arguments for a module to an argparse parser."""
    cli_args = module_config[module_name]["cli_args"]
    for arg in cli_args:
        parser.add_argument(arg["name"], help=arg["help"], required=arg["required"])


from typing import Optional
import logging

logger = logging.getLogger(__name__)

def submit_module(api_manager: APIManager, module: str, **kwargs) -> Optional[str]:
    """
    Submits a module with the provided arguments and returns the job number.
    :param api_manager: Instance of APIManager to handle submission.
    :param module: Name of the module to submit.
    :param kwargs: Module-specific arguments.
    :return: Submitted job number, or None on failure.
    """
    def path_to_payload(path: str):
        """Helper to open a file in binary mode for uploading."""
        try:
            return open(path, "rb")
        except FileNotFoundError:
            logger.error(f"File not found: {path}")
            return None

    # Load module-specific configuration
    if module not in MODULE_CONFIG:
        logger.error(f"Unknown module: {module}")
        return None

    config = MODULE_CONFIG[module]
    files = {}

    try:
        # Prepare required files
        for file_arg, payload_name in config.get("required_files", {}).items():
            if file_arg not in kwargs or not kwargs[file_arg]:
                logger.error(f"Missing required file: {file_arg}")
                return None

            file_obj = path_to_payload(kwargs[file_arg])
            if not file_obj:
                return None  # Error logged by `path_to_payload`

            files[payload_name] = (None, file_obj)

        # Add optional parameters
        for optional_arg in config.get("optional", []):
            if optional_arg in kwargs and kwargs[optional_arg]:
                files[optional_arg] = (None, kwargs[optional_arg])

        # Submit the module
        response = api_manager.post_request(
            TLDREndpoints.get_endpoint(config["endpoint"]), files=files
        )

        return response

    except Exception as e:
        logger.error(f"Error during submission: {e}")
        return None

    finally:
        # Ensure all file handles are closed
        for key, value in files.items():
            if isinstance(value, tuple) and hasattr(value[1], "close"):
                value[1].close()


def add_module_arguments(parser, module_name, module_config):
    """Dynamically add arguments based on module config."""
    module = module_config.get(module_name, {})
    if not module:
        raise ValueError(f"Module {module_name} not found in the configuration.")

    # Add arguments specified in cli_args
    for arg in module.get("cli_args", []):
        parser.add_argument(
            arg["name"], 
            type=str, 
            required=arg.get("required", False), 
            help=arg.get("help", "No description provided.")
        )

def main():
    parser = argparse.ArgumentParser(description="Submit and manage docking tasks via TLDR API.")
    parser.add_argument("--list-modules", action="store_true", help="List all available modules and exit.")
    parser.add_argument("--module", choices=MODULE_CONFIG.keys(), help="Module type to submit.")
    parser.add_argument("--job-number", help="Job number to check status.")
    parser.add_argument("--output-dir", default="decoys", help="Directory to store downloaded decoys.")
    
    args, unknown_args = parser.parse_known_args() 

    api_manager = APIManager()  # Initialize API manager

    # Handle listing modules
    if args.list_modules:
        print("Available modules:")
        for module_name, config in MODULE_CONFIG.items():
            print(f"- {module_name}: {config['description']}")
            for arg in config.get("cli_args", []):
                print(f"   {arg['name']} - {arg.get('help', 'No description provided.')}")
        return 

    # # Handle job status check
    # if args.job_number:
    #     check_job_status(api_manager, args.job_number)
    #     return

    # Add dynamic arguments for the selected module
    module_name = args.module
    if not module_name:
        parser.error("You must specify a module using --module.")
    
    module_parser = argparse.ArgumentParser()
    add_module_arguments(module_parser, module_name, MODULE_CONFIG)
    
    # Parse remaining arguments for the module
    module_args = module_parser.parse_args(unknown_args)

    # Submit the module
    response = submit_module(api_manager, module_name, **vars(module_args))  # Unpack the args dictionary

    if response.text:
        logger.info("Job submitted, but unsure if it went through (this is expected). Checking if identified job is running...")
        submitted_job = api_manager.url_to_job_no(response.url)
        job_status = check_job_status(api_manager, submitted_job)

        print(job_status)
        
        if job_status in ['Submitted', 'Running']:
            logger.info(f"Job {submitted_job} is {job_status} and submitted successfully!")
        else:
            logger.error(f"Job {submitted_job} status is unrecognized: {job_status}.")
    else:
        logger.error("Job failed to submit.")


if __name__ == "__main__":
    main()