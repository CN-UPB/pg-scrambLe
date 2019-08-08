# son-bss  [![Build Status](http://jenkins.sonata-nfv.eu/buildStatus/icon?job=son-bss)](http://jenkins.sonata-nfv.eu/job/son-bss)

Very simple gui that allows customers to retrieve and inspect Network Services and additionally allows to request instantiations on them.

## Development

sudo docker stop son-bss
sudo docker rm son-bss
sudo docker build -t son-bss -f Dockerfile .

sudo docker run -d --name son-bss --net=son-sp --network-alias=son-bss -p 25001:1337 -p 25002:1338 -v $(pwd)/code/app/modules:/usr/local/bss/code/app/modules son-bss grunt serve:integration --gkApiUrl=http://192.168.122.223/api/v2 --hostname=0.0.0.0 --userManagementEnabled=true --licenseManagementEnabled=true --debug

sudo docker logs son-bss -f

 son-gui
