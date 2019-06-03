# son-gui  [![Build Status](http://jenkins.sonata-nfv.eu/buildStatus/icon?job=son-gui)](http://jenkins.sonata-nfv.eu/job/son-gui) 

Gatekeeper GUI designed to cover the needs of the two user groups, service developers and platform administrators in supporting the process of DevOps in SONATA. Gatekeeper GUI is an API management and visualization tool that on one hand enables SONATA developers to manage their services throughout their whole lifecycle, while on the other hand offer Service Platform administrator the ability to provision, monitor and monetize platform resourcess.

## Development

## Installation

cd son-gui

sudo docker stop son-gui
sudo docker rm son-gui
sudo docker build -t son-gui .
sudo docker run -d --net=son-sp --name son-gui son-gui

sudo docker logs son-gui -f

sudo docker exec -it son-gui bash


# Dev

sudo docker run -d --name scalingplugin --net=son-sp --network-alias=scalingplugin -v $(pwd)/plugins/son-mano-scaling:/plugins/son-mano-scaling scalingplugin




cd son-gui

sudo docker stop son-gui
sudo docker rm son-gui
sudo docker build -f Dockerfile-dev -t son-gui .
sudo docker run -d --net=son-sp --name son-gui -v $(pwd):/var/www/html son-gui

sudo docker logs son-gui -f
