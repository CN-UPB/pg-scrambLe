# SONATA's scalingplugin plugin

## How to run it

* (follow the general README.md of this repository to setup and test your environment)
* To run the scalingplugin locally, you need:
 * a running RabbitMQ broker (see general README.md of this repo for info on how to do this)
 * a running plugin manager connected to the broker (see general README.md of this repo for info on how to do this)
 
* Run the Scalingplugin (in a Docker container):
 * (do in `son-mano-framework/`)
 * `docker build -t scalingplugin -f plugins/son-mano-scaling/Dockerfile .`
 * `docker run --name scalingplugin --net=son-sp --network-alias=scalingplugin scalingplugin`
 * to rebuild `docker rm scalingplugin`
 


sudo docker stop scalingplugin
sudo docker rm scalingplugin
sudo docker build -t scalingplugin -f plugins/son-mano-scaling/Dockerfile .
sudo docker run --name scalingplugin --net=son-sp --network-alias=scalingplugin scalingplugin

# Dev

sudo docker stop scalingplugin
sudo docker rm scalingplugin
sudo docker build -t scalingplugin -f plugins/son-mano-scaling/Dockerfile-dev .
sudo docker run -d --name scalingplugin --net=son-sp --network-alias=scalingplugin -v $(pwd)/plugins/son-mano-scaling:/plugins/son-mano-scaling scalingplugin
sudo docker logs scalingplugin -f