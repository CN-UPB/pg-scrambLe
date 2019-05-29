# Adaptor

Documentation is available here - [ReadtheDocs](https://python-mano-wrappers.readthedocs.io/en/adaptor/).

## Structure

+ `adaptor.py` - Entry point for utilizing the underlying wrappers

+ `wrappers` - Contains REST wrappers for MANO frameworks 
    - `CommonInterfaces` - Starting point Python Module for implementation that defines an abstract base class according to the ETSI standard
    - `OSMClient` - REST wrapper for OpenSource Mano based
    - `SONATAClient` - REST wrapper for Sonata based

+ `tests` - Contains test cases for individual wrappers

+ `samples` - Contains sample files needed for testing

## Development

1. Docker compose up from the `src` folder (Detailed instructions in the root README)

    + `docker-compose -f "docker-compose.dev.yml" up -d --build`

2. Once the containers are running, docker attach to the adaptor image to get terminal access
    + Run `docker ps` and copy the container id for src_adaptor image (ex. 1ffb536c1a8e)
    + Run  `docker exec -it <PASTE_ID_HERE> /bin/sh -c "[ -e /bin/bash] && /bin/bash || /bin/sh"` with your id <PASTE_ID_HERE> to get terminal access
        + Run `ls` to confirm access

3. Run test cases from the container
    + Run `py.test` to execute all test cases
    + Run `clear && py.test -s tests/osm/test_auth.py` to run all test cases in a file, in this case osm - test_auth.py
    + Run `clear && py.test -s tests/osm/test_auth.py::test_auth` to run one specific test case in a file, in this case osm - test_auth
