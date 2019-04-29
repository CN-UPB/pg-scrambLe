## Custom Load Balancing NS
+ OSM Schema - http://osm-download.etsi.org/ftp/osm-doc/vnfd.html

+ Useful OSM Documents FTP - http://osm-download.etsi.org/ftp/

+ Useful for making NS - http://osm-download.etsi.org/ftp/osm-5.0-five/5th-hackfest/presentations/5th%20OSM%20Hackfest%20-%20Session%202%20-%20Creating%20a%20basic%20VNF%20and%20NS.pdf

+ OSM Devops repo - https://osm.etsi.org/gitweb/?p=osm/devops.git;a=summary

+ Online guide for vnffg? - https://wiki.opnfv.org/display/sfc/OSM+guide

+ Multi NIC VM image - https://leadwithoutatitle.wordpress.com/2017/07/06/how-to-create-a-multi-nic-ubuntu-cloud-image/

+ Multi NIC ubuntu interfaces settings - https://askubuntu.com/questions/868942/how-to-configure-2-network-interfaces-with-different-gateways 

+ Preparing virtual image

virt-sysprep -a ubuntu-16.04-server-cloudimg-amd64-disk1.img --root-password password:12345 --ssh-inject root:file:/home/ashwin/.ssh/id_rsa.pub

+ qemu-img convert -O qcow2 -c source.qcow2 dest.qcow2
----

Devstack Requirements

+ Create a new user and assign a project in devstack, while doing so, assign max quotas

+ Create custom routers and two private networks "mgmt" and "datanet" and relevant subnets. make sure the subnets are added to the routers interfaces 

+ "datanet" ip range - 172.17.17.0/26 

+ Upload ubuntu cloud 16.04 image under the name "ubuntu-cloud". Image can be downloaded here - use qcow2 format
    - https://cloud-images.ubuntu.com/releases/16.04/release/

----

