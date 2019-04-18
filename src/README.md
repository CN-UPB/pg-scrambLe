# Project source code

## Initial setup

Clone this repository and checkout to `develop` branch

1. Install docker
    + https://docs.docker.com/install/

2. Install Docker Compose
    + https://docs.docker.com/compose/install/

3. Run Docker Image to start services
    + cd into `src` folder from terminal
    + While developing run `docker-compose f docker-compose.dev.yml up --build`
        + Running this will restart the service on change
    + run `docker-compose up`
        + rerun after making changes `docker-compose up --build`

4. Test if the services are running
    + Open
        + `http://localhost:8000/translator/hello/myname`
        + `http://localhost:8000/splitter/hello/myname`
        + `http://localhost:8000/adaptor/hello/myname`