#!/usr/bin/env bash

dir=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

# IP_BSS="131.234.29.102"

echo "$dir"

echo "Starting Scramble SRV.."
cd "$dir/son-gkeeper/son-gtksrv"

sudo docker stop son-gtksrv
sudo docker rm son-gtksrv
sudo docker build -t son-gtksrv -f Dockerfile .

sudo docker run -d --name son-gtksrv --net=son-sp --network-alias=son-gtksrv -p 5300:5300 son-gtksrv

echo "##############################################"
echo "##############################################"

echo "Starting Scramble BSS.."
cd "$dir/son-bss"
echo "$(pwd)"

sudo docker stop son-bss
sudo docker rm son-bss
sudo docker build -t son-bss -f Dockerfile .

sudo docker run -d --name son-bss --net=son-sp --network-alias=son-bss -p 25001:1337 -p 25002:1338 -v $(pwd)/code/app/modules:/usr/local/bss/code/app/modules son-bss grunt serve:integration --gkApiUrl=http://131.234.29.140/api/v2 --hostname=0.0.0.0 --userManagementEnabled=true --licenseManagementEnabled=true --debug

echo "##############################################"
echo "##############################################"

cd "$dir/son-mano-framework"
echo "$(pwd)"

echo "Starting Scramble SLM.."

sudo docker stop servicelifecyclemanagement
sudo docker rm servicelifecyclemanagement
sudo docker build -t servicelifecyclemanagement -f plugins/son-mano-service-lifecycle-management/Dockerfile-dev .
sudo docker run -d --name servicelifecyclemanagement --net=son-sp --network-alias=servicelifecyclemanagement -v $(pwd)/plugins/son-mano-service-lifecycle-management:/plugins/son-mano-service-lifecycle-management servicelifecyclemanagement

echo "##############################################"
echo "##############################################"

echo "Starting Scramble Scaling.."
sudo docker stop scalingplugin
sudo docker rm scalingplugin
sudo docker build -t scalingplugin -f plugins/son-mano-scaling/Dockerfile-dev .
sudo docker run -d --name scalingplugin --net=son-sp --network-alias=scalingplugin -v $(pwd)/plugins/son-mano-scaling:/plugins/son-mano-scaling scalingplugin
