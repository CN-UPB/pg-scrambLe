# SONATA's service lifecycle manager plugin
Service Lifecycle Manager: Component in the SONATA framework that is responsible to manage the lifecycle of the deployed services.

## Requires
* Docker

## Implementation
* implemented in Python 3.4
* dependecies: amqp-storm
* The main implementation can be found in: `son_mano_slm/slm.py`

## How to run it

```
sudo docker stop servicelifecyclemanagement
sudo docker rm servicelifecyclemanagement
sudo docker build -t servicelifecyclemanagement -f plugins/son-mano-service-lifecycle-management/Dockerfile .
sudo docker run -d --name servicelifecyclemanagement --net=son-sp --network-alias=servicelifecyclemanagement servicelifecyclemanagement

sudo docker logs servicelifecyclemanagement -f
```

### In Development

```
sudo docker stop servicelifecyclemanagement
sudo docker rm servicelifecyclemanagement
sudo docker build -t servicelifecyclemanagement -f plugins/son-mano-service-lifecycle-management/Dockerfile-dev .
sudo docker run -d --name servicelifecyclemanagement --net=son-sp --network-alias=servicelifecyclemanagement -v $(pwd)/plugins/son-mano-service-lifecycle-management:/plugins/son-mano-service-lifecycle-management servicelifecyclemanagement

sudo docker logs servicelifecyclemanagement -f
```