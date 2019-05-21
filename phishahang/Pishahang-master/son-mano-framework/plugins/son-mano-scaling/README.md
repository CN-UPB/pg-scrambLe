# SONATA's Scramble plugin

## How to run it

* (follow the general README.md of this repository to setup and test your environment)
* To run the Scramble locally, you need:
 * a running RabbitMQ broker (see general README.md of this repo for info on how to do this)
 * a running plugin manager connected to the broker (see general README.md of this repo for info on how to do this)
 
* Run the Scramble (in a Docker container):
 * (do in `son-mano-framework/`)
 * `docker build -t scramble -f plugins/son-mano-scaling/Dockerfile .`
 * `docker run --name scalingplugin --net=son-sp --network-alias=scalingplugin scalingplugin`
 * to rebuild `docker rm scalingplugin`
 


sudo docker stop scalingplugin
sudo docker rm scalingplugin
sudo docker build -t scramble -f plugins/son-scramble-plugin/Dockerfile .
sudo docker run --name scalingplugin --net=son-sp --network-alias=scalingplugin scramble