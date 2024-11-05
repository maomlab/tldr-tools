## What is it?

A toolkit to interface [https://tldr.docking.org/](https://tldr.docking.org/), a webserver home to a collection of docking optimization and benchmark molecular docking programs.

## Installation

Installation is super easy and pip installable. Pleaes make sure you have Python 3.6 installed.

```shell-session
$ pip install tldr-tools
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

Documenting runs with the optional memo parameter is encouraged.

Pass in a job number to check on a status of a run:
```shell-session
tldr-status --job-number 14886
```

Once a run is successful, you can download the output to a local directory:

```shell-session
tldr-download --job-number 14886 --output some_folder
```

## Extending tldr-tools

Community and expansion is encouraged and made easy with this codebase. Adding new modules that are newly introduced on https://tldr.docking.org/ is painless, and is as simple as adding a new Endpoint and required/optional list of files.