## What is it?

A toolkit to interface [https://tldr.docking.org/](https://tldr.docking.org/), a webserver home to a collection of docking optimization and benchmark molecular docking programs.

## Installation

Installation is super easy and pip installable. Please make sure you have Python 3.6 installed.

```shell-session
$ pip install tldr-tools
```

The API_KEY, as found on the top right corner under tldr.docking.org, must be set as an environmental variable before usage. The API_KEY can be assigned in .env under the package root, or directly set in terminal.

```shell-session
# Method 1: Add under .env (recommended for for python notebooks)
$ echo "API_KEY=SOMESECRETKEY" > .env

# Method 2: Manually setting API_KEY (recommended for interactive jobs)
export API_KEY="SOMESECRETKEY"
```

## Usage
To view the current implemented modules in tldr-tools, please run:

```shell-session
$ tldr-submit --list-modules
```

For example, if running decoy generation is desired:

```shell-session
tldr-submit --module decoys --activesism input_files/actives.ism --decoygenin input_files/decoy_generation.in --memo "Decoy generation for ADA, replicate 1"
```

Or, you can build a ligand using DOCK38:

```shell-session
tldr-submit --module build --input chaff_tools/aggregator_advisor_hf_test.txt --memo "aa_hf_test"
```

Documenting runs with the optional memo parameter is encouraged.

Pass in a job number to check on a status of a run:
```shell-session
tldr-status --job-number 14886
```

Once a run is successful, you can download the output to a local directory:

```shell-session
tldr-download --job-number 14886 --output some_folder
```

## Does tldr-tools work in Colab and Jupyter Notebook?

Yep, you use tldr-tools as follow:

```shell-session
from tldr_tools.tldr_submit import *        # Import to submit new jobs
from tldr_tools.tldr_endpoint import *      # Import for APIManager() which is responsible for handling requests (api_token and headers)
from tldr_tools.tldr_status import *        # Import to check on status

api_manager = APIManager()
module_name = "build"

kwargs = {
   "input": "aggregator_advisor_hf_test.txt",
   "memo": "aa_hf_test"
}

# Submit the module
job_number = submit_module(api_manager, module_name, **kwargs)
```

## Extending tldr-tools

Community and expansion is encouraged and made easy with this codebase. Adding new modules that are newly introduced on https://tldr.docking.org/ is painless, and is as simple as adding a new Endpoint and required/optional list of files.