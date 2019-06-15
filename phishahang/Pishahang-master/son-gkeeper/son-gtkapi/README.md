# [SONATA](http://www.sonata-nfv.eu)'s Gatekeeper API micro-service

# Build

cd pg-scrambLe/phishahang/Pishahang-master/son-gkeeper/son-gtkapi

sudo docker stop son-gtkapi
sudo docker rm son-gtkapi
sudo docker build -t son-gtkapi -f Dockerfile .
sudo docker run -d --name son-gtkapi --net=son-sp --network-alias=son-gtkapi -p 32001:5000 son-gtkapi
sudo docker logs son-gtkapi -f


-v $(pwd):/app 