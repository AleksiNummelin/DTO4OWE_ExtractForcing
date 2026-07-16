This repository contains combination of python and shell scripts to facilitate download of Climate DT data using the polytope interface.

Quick HOWTO

1) Make sure you have registered at https://platform.destine.eu/ and requested the upgraded access
2) Make sure you have setup a python environment with all the packages required by polytope https://polytope.readthedocs.io/en/latest/Service/Installation/
3) Once the enviroment is setup, one can modify the parameters to be downloaded in the extract_forcing.py file (at the moment the set of surface parameters will work, some of the other parameter sets are waiting for polytope updates, see https://github.com/ecmwf/polytope/issues/531), and then control the years to be downloaded in the run_extract_forcing.sh
4) In order for the download to work, one needs to run desp-authentication.py before starting the download (will store credentials to your local computer, they will be valid for some time before expiring).
