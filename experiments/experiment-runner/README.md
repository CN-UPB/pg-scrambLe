# Experiment Runner


http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.cpu&after=-60&format=datasource&options=nonzero

http://vm-hadik3r-06.cs.uni-paderborn.de:19999/api/v1/data?chart=system.cpu&format=json&points=500&after=1558810800&before=1558812600&options=jsonwrap


cd into experiments/experiment-runner

sudo docker stop experiment-runner
sudo docker rm experiment-runner
sudo docker build -t experiment-runner -f Dockerfile-dev .

sudo docker run -d --name experiment-runner -p 9000:9000 -v $(pwd):/app \
    -v /var/run/docker.sock:/container/path/docker.sock \
    -v /home/sonatamano/pg-scrambLe/phishahang/Pishahang-master/son-mano-framework/plugins/son-mano-scaling/debugnorm:/debugscale \
    experiment-runner

sudo docker exec -it experiment-runner bash

sudo docker logs experiment-runner -f

# Attach shell
sudo docker exec -it experiment-runner bash

# Background Run 
nohup python -u ./run-experiment-osm.py > experiment.log &
nohup python -u ./run-experiment-sonata.py > experiment.log &
nohup python -u ./run-experiment-sonata-k8-scaling.py > 10xpc-experiment.log &