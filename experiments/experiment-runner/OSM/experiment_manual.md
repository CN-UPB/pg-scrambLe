## Experiment Steps

+ Upload VNF image(cirros/ubuntu) in Openstack
+ Upload NSD and VNFD in OSM MANO
+ Build and run the `experiment-runner` docker container on the MANO host
+ Change the `NSDESCRIPTION` in `run-experiment-osm.py` according to the following naming convention: "`<NSNAME>_<NO_INSTANCES>_Run<ID>`"
+ Start a bash session inside the container and start the `run-experiment-osm.py` script. 
+ The results are collected in a CSV format in the specific folder and be found at the end of the experiment run. The graphs can be visualized in an interactive html. 
