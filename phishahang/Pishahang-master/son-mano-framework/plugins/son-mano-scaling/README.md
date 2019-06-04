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

sudo docker exec -it scalingplugin bash
cd son_mano_scaling
python

from son_mano_scaling.mano_manager import ManoManager
from son_mano_scaling.config import *
import json

mano_manager = ManoManager()
#_instance_id = json.loads(mano_manager.create_pishahang_instance())
_instance_id = mano_manager.create_osm_instance()

if _instance_id:
    _instance_id = json.loads(_instance_id["data"])
else:
    pass


_token = json.loads(mano_manager.sonata_auth.auth(username=PISHAHANG_DEFAULT_USERNAME, password=PISHAHANG_DEFAULT_PASSWORD))
_token = json.loads(_token["data"])

nsr_payload = json.loads(mano_manager.sonata_nslcm.get_ns_instances(token=_token["token"]["access_token"]))
nsr_payload = json.loads(nsr_payload["data"])

for nsr in nsr_payload:
    print(nsr["descriptor_reference"])
    if nsr['descriptor_reference'] == _instance_id["service_uuid"]:
        for vnfr in nsr['network_functions']:
            vnfr_uuid = vnfr['vnfr_id']

print(vnfr_uuid)

# Dev

sudo docker stop scalingplugin
sudo docker rm scalingplugin
sudo docker build -t scalingplugin -f plugins/son-mano-scaling/Dockerfile-dev .
sudo docker run -d --name scalingplugin --net=son-sp --network-alias=scalingplugin -v $(pwd)/plugins/son-mano-scaling:/plugins/son-mano-scaling scalingplugin
sudo docker logs scalingplugin -f



# Debugging

+ instantiate request
{'error': False, 'data': '{"id":"76db5919-8e1b-41a7-a18d-f4eb4319b855","created_at":"2019-06-04T11:29:56.092Z","updated_at":"2019-06-04T11:29:56.092Z","service_uuid":"a888ccbb-bfa8-4a3a-bbcb-99b3af197a17","status":"NEW","request_type":"CREATE","service_instance_uuid":null,"began_at":"2019-06-04T11:29:56.087Z","callback":"http://son-gtkkpi:5400/service-instantiation-time"}'}

+ NSR list
[
    
{'network_functions': [{'vnfr_id': 'd544d05f-7c4a-4a20-9e4b-e87d03b28400'}], 'descriptor_reference': '8636143c-a033-4f77-8c7c-aa015e8753c5', 'created_at': '2019-06-03T16:50:05.870+00:00', 'updated_at': '2019-06-03T16:50:05.870+00:00', 'uuid': '8e3e30a1-7c2c-4b08-a5a2-5e4decafa272', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': '381b6b91-8713-4980-ac51-29454475b1a5'}], 'descriptor_reference': '8a1a57d6-9f0f-462a-853a-11eaec83b71e', 'created_at': '2019-06-03T20:44:59.682+00:00', 'updated_at': '2019-06-03T20:44:59.682+00:00', 'uuid': '917e3540-2bc4-40f2-9ce1-d9f4f6a736e1', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': 'e33ab498-941b-492b-a291-5c3cd71e2f05'}], 'descriptor_reference': 'f346eb01-07b2-4785-879d-1a7c4d3a3db4', 'created_at': '2019-06-03T20:46:15.884+00:00', 'updated_at': '2019-06-03T20:46:15.884+00:00', 'uuid': '3fa94279-7f63-425b-ae91-04e44cc5ee95', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': '7d875447-7e66-4dfd-ab55-6c8dc36e6ae2'}], 'descriptor_reference': '704acd1f-da9c-45d8-a6c9-e1cf927d670c', 'created_at': '2019-06-03T20:51:16.781+00:00', 'updated_at': '2019-06-03T20:51:16.781+00:00', 'uuid': '4b0cfb75-aaa4-4653-a621-5e0621453648', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': 'b407bde8-5879-42d7-b706-3170fbfc973a'}], 'descriptor_reference': '704acd1f-da9c-45d8-a6c9-e1cf927d670c', 'created_at': '2019-06-03T21:01:20.710+00:00', 'updated_at': '2019-06-03T21:01:20.710+00:00', 'uuid': 'bea74654-faa6-4ab5-90ce-b608e507f059', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': '82045a58-9c3c-4487-9f77-f33ac064853d'}], 'descriptor_reference': '5711258f-a0ca-44b4-915c-8d126d164c01', 'created_at': '2019-06-03T21:26:13.725+00:00', 'updated_at': '2019-06-03T21:26:13.725+00:00', 'uuid': '070d1f4b-35d6-48d0-b3be-0f77411f7c03', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': '969fa3b9-3ff6-42f5-ae14-d428b17a43b7'}], 'descriptor_reference': '5711258f-a0ca-44b4-915c-8d126d164c01', 'created_at': '2019-06-03T21:28:52.915+00:00', 'updated_at': '2019-06-03T21:28:52.915+00:00', 'uuid': '1633f54d-f6c9-4100-bc42-5c6ab4e54f1a', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': 'cd011339-3bd0-42c5-9a10-41bbdad27411'}], 'descriptor_reference': '5711258f-a0ca-44b4-915c-8d126d164c01', 'created_at': '2019-06-03T22:04:30.669+00:00', 'updated_at': '2019-06-03T22:04:30.669+00:00', 'uuid': '1c2a05ec-9860-478a-b8d3-08d606d813f7', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': '5163a801-5475-4617-ad36-389308e2abff'}], 'descriptor_reference': '2d9f88d5-126d-4177-9f98-ebeb0988d39c', 'created_at': '2019-06-03T22:17:46.534+00:00', 'updated_at': '2019-06-03T22:17:46.534+00:00', 'uuid': '5889be0d-dc64-47a9-adb1-3ad013e70269', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}, 

{'network_functions': [{'vnfr_id': '6cf5d402-6647-44a4-ad4f-69cbe465d3a5'}], 'descriptor_reference': '8ec39d3b-395d-4820-94c1-eabd43bd3180', 'created_at': '2019-06-03T22:34:30.324+00:00', 'updated_at': '2019-06-03T22:34:30.324+00:00', 'uuid': 'f8a0ec6d-2253-47c0-8325-0d9f8fa35a54', 'version': '1', 'status': 'normal operation', 'descriptor_version': 'nsr-schema-01'}]