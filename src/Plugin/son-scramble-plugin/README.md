# SONATA's Scramble plugin

## How to run it

* (follow the general README.md of this repository to setup and test your environment)
* To run the Scramble locally, you need:
 * a running RabbitMQ broker (see general README.md of this repo for info on how to do this)
 * a running plugin manager connected to the broker (see general README.md of this repo for info on how to do this)
 
* Run the Scramble (in a Docker container):
 * (do in `son-mano-framework/`)
 * `docker build -t scramble -f plugins/son-scramble-plugin/Dockerfile .`
 * `docker run --name scrambleplugin --net=son-sp --network-alias=scrambleplugin scramble`
 * to rebuild `docker rm scrambleplugin`
 


sudo docker stop scrambleplugin
sudo docker rm scrambleplugin
sudo docker build -t scramble -f plugins/son-scramble-plugin/Dockerfile .
sudo docker run --name scrambleplugin --net=son-sp --network-alias=scrambleplugin scramble

## Output
The output of the Scramble plugin should look like this:

```
INFO:son-mano-base:plugin:Starting MANO Plugin: 'son-plugin.ScramblePlugin' ...
INFO:son-mano-base:plugin:Plugin connected to broker.
INFO:plugin:scramble:Subscribed to topic: mano.service.scramble
INFO:son-mano-base:plugin:Plugin registered with UUID: '41f81920-d817-4738-822b-b1a7b0e4a585'
INFO:plugin:scramble:Scramble plugin started and operational.
```

It shows how the Scramble plugin connects to the broker, registers itself to the plugin manager and receives the lifecycle start event.

