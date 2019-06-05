# import wrappers
# make method which does the following, take mano as parameter

# get start time
# sleep 5 min
# get NS instantiation time
# send instantiation request to osm/sonata

import wrappers
import time
nsName = "stress_case1"
nsDescription = "NSDESCRIPTION"
nsdId = "stress_case1-ns"
vimAccountId = "openstack"

start_time = int(time.time())
time.sleep(5)
print (start_time)

ns_inst_time = int(time.time())

wrappers.OSMClient.nslcm.Nslcm.post_ns_instances_nsinstanceid_instantiate(self, token, nsDescription,
                                 nsName, nsdId, vimAccountId, host=None, port=None)
time.sleep(20)
ns_term_time = int(time.time())                                 

print(ns_inst_time)
print(ns_term_time)






