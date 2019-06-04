# Experiment Runner


http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.cpu&after=-60&format=datasource&options=nonzero

http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.cpu&format=json&points=500&after=1558810800&before=1558812600&options=jsonwrap


cd into experiments/experiment-runner

sudo docker stop experiment-runner
sudo docker rm experiment-runner
sudo docker build -t experiment-runner -f Dockerfile-dev .
sudo docker run -d --name experiment-runner -p 9000:9000 -v $(pwd):/app -v /var/run/docker.sock:/container/path/docker.sock experiment-runner

sudo docker logs experiment-runner -f

sudo docker exec -it experiment-runner bash

import docker
client = docker.DockerClient(base_url='unix://container/path/docker.sock')
client.containers.list()

client.containers.list()[0].attrs["Id"]
client.containers.list()[0].attrs["Name"]