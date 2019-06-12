## Openstack installation

+ Step 1 : create user 

+ Step 2 : go to
https://github.com/CN-UPB/Pishahang/blob/master/osm/documentation/devstack/local.conf
          and copy local.conf and nano to it and paste it. change IPs to VIMs IP and save
          ./stack.sh


#cloud-config

ssh_authorized_keys:
  - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDGWi9IsfOpCz4hNSo02j/GpB/gQ7seZeNSSKuqjlUfUZOGyptgV9HMvOKVRVzMhn3Wbww4ShPCC7k5OreRveTWGj1lj1peqc8tSk+zP/oiFqT5VoKqLHBKVtR/+yx+GRCDPkrqYBY9OhNKaY6P+JJBNks72m93+UGaXZClpmD3xNPul6TdkkjmoTjOq4MAqHsudPoQx4TrLsTEhEusKcapGmm4oJL2x3OfdhCi6cjnVa271LiUWeBvNvlwewhdGidJ4ziUAAkCual9nc+YkdMS46x2nzvXDWcSGqV/PHSpWwM9B3PmzH0T/bps2g7UqGbWDKR6D1zwZqYao77d2ylj osmvim@osmvim



openstack security group rule create --proto icmp --dst-port 0 default
openstack security group rule create --proto tcp --dst-port 22 default
nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0
nova secgroup-add-rule default tcp 22 22 0.0.0.0/0

stress -d 2 --hdd-bytes 512M
stress -c 2 -m 1 -d 1 --hdd-bytes 512M -t 10s

NOTES

+ install osm , openstack and netdata
+ Modifications to NSDs and VNFDs

## Terminal
+ ssh into vim
+ ssh keygen
+ cat ~/.ssh/id_rsa.pub
+ ssh ubuntu@192.168.23.109(F IP from instances)
+ ifconfig (for eth0)
+ sudo iptables -t nat -A POSTROUTING -o ens160 -j MASQUERADE
+ nano os.auth (content from R3 file from openstack)
+ source os.auth
+
+
+ (commands from Configure guest VM connectivity, pishahang - github)
+ sudo apt update
+ sudo apt-get install stress
+ cron cmd to schedule stress -c 2 -m 1 -d 1 --hdd-bytes 512M -t 10s
+ volume snapshot to image ## http://khmel.org/?p=1188
+ delete instances,volumes and images in openstack
+ tag vim in osm
+ instantiate ns 
+ check the instances in mano and vim to be running

## VIM
+ Ubuntu image created and launched
+ Instances launced (script! NTF)
   - Associate floating IPs

important links

## convert instance to image

 https://docs.openstack.org/cinder/latest/admin/blockstorage-volume-backed-image.html#creating-a-volume-backed-image

## stress tool 

https://www.hecticgeek.com/2012/11/stress-test-your-ubuntu-computer-with-stress/ 

## pishahang github

https://github.com/CN-UPB/Pishahang/tree/master/osm/documentation

##  netdata installation guide

https://docs.netdata.cloud/packaging/installer/

## swagger

https://editor.swagger.io/?url=https://raw.githubusercontent.com/netdata/netdata/master/web/api/netdata-swagger.yaml#

