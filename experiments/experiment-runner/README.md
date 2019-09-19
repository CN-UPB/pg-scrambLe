# Experiment Runner

MANO Benchmarking Framework (MBF) is a result of a small script that was used to run the experiments as part of the pg-scramble project. The idea of MBF is to provide MANO developers with a generic framework for running experiments on MANO. MBF mainly provides the following 


1. Easy interfacing with MANO instances by using `python-mano-wrappers`
2. Ability to run experiments with different service descriptors
3. Collection of performance metrics in convenient data format
4. Flexible graphing mechanism of the collected data. 


# Steps to run an experiment

    # The following commands are to be run on the machine where the MANO is installed (Remote experiment support to be added soon)

    # Clone the repository
    git clone git@github.com:CN-UPB/pg-scrambLe.git --branch scalability-experiments experiments

    # cd into the right folder
    cd experiments/experiment-runner

    # Delete any previous builds and run the following commands
    sudo docker stop experiment-runner
    sudo docker rm experiment-runner
    sudo docker build -t experiment-runner -f Dockerfile-dev .

    # Run docker container and attach docker.sock as volume, so that we have access to docker API
    sudo docker run -d --name experiment-runner -p 9000:9000 -v $(pwd):/app \
        -v /var/run/docker.sock:/container/path/docker.sock \
        experiment-runner

    # get a bash session inside the container
    sudo docker exec -it experiment-runner bash

    # Background Run the respective experiment file
    nohup python -u ./run-experiment-osm.py > experiment.log &
    nohup python -u ./run-experiment-sonata.py > experiment.log &
    nohup python -u ./run-experiment-sonata-k8-scaling.py > 10xpc-experiment.log &


# Additional commands

    # To show logs 
    sudo docker logs experiment-runner -f

    # This is for testing scaling plugin
    sudo docker run -d --name experiment-runner -p 9000:9000 -v $(pwd):/app \
        -v /var/run/docker.sock:/container/path/docker.sock \
        -v /home/sonatamano/pg-scrambLe/phishahang/Pishahang-master/son-mano-framework/plugins/son-mano-scaling/debugnorm:/debugscale \
        experiment-runner
