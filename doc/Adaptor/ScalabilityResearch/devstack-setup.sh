sudo apt-get update
sudo apt-get install -y git

sudo useradd -s /bin/bash -d /opt/stack -m stack
echo "stack ALL=(ALL) NOPASSWD: ALL" \
    | sudo tee /etc/sudoers.d/stack

sudo su - stack
git clone https://git.openstack.org/openstack-dev/devstack
cd devstack
git checkout stable/ocata

131.234.29.169

---












[[local|localrc]]


ADMIN_PASSWORD=123
DATABASE_PASSWORD=123
RABBIT_PASSWORD=123
SERVICE_PASSWORD=$ADMIN_PASSWORD

[[local|localrc]]
HOST_IP=131.234.29.169
SERVICE_HOST=131.234.29.169
MYSQL_HOST=131.234.29.169
RABBIT_HOST=131.234.29.169
GLANCE_HOSTPORT=131.234.29.169:9292


LOGFILE=$DEST/logs/stack.sh.log
LOGDAYS=2


CINDER_BRANCH=stable/ocata
GLANCE_BRANCH=stable/ocata
HORIZON_BRANCH=stable/ocata
KEYSTONE_BRANCH=stable/ocata
KEYSTONECLIENT_BRANCH=stable/ocata
NOVA_BRANCH=stable/ocata
NOVACLIENT_BRANCH=stable/ocata
NEUTRON_BRANCH=stable/ocata
SWIFT_BRANCH=stable/ocata


SWIFT_HASH=66a3d6b56c1f479c8b4e70ab5c2000f5
SWIFT_REPLICAS=1

SWIFT_DATA_DIR=$DEST/data

enable_plugin heat https://git.openstack.org/openstack/heat stable/ocata
enable_plugin networking-sfc https://git.openstack.org/openstack/networking-sfc stable/ocata

## Neutron options
Q_USE_SECGROUP=False
FLOATING_RANGE="172.16.19.0/24"
IPV4_ADDRS_SAFE_TO_USE="10.0.0.0/24"
Q_FLOATING_ALLOCATION_POOL=start=172.16.19.151,end=172.16.19.200
PUBLIC_NETWORK_GATEWAY=172.16.19.1
PUBLIC_INTERFACE=ens160

# Open vSwitch provider networking configuration
Q_USE_PROVIDERNET_FOR_PUBLIC=True
OVS_PHYSICAL_BRIDGE=br-ex
PUBLIC_BRIDGE=br-ex
OVS_BRIDGE_MAPPINGS=public:br-ex


VOLUME_BACKING_FILE_SIZE=1800000M

[[post-config|$NOVA_CONF]]
[DEFAULT]
block_device_allocate_retries=6000
block_device_allocate_retries_interval=1
security_group_api=nova
firewall_driver=nova.virt.firewall.NoopFirewallDriver

# After devstack
# openstack security group rule create --proto icmp --dst-port 0 default
# openstack security group rule create --proto tcp --dst-port 22 default
# nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0
# nova secgroup-add-rule default tcp 22 22 0.0.0.0/0

# sudo iptables -t nat -A POSTROUTING -o br-ex -j MASQUERADE

# neutron net-create large-priv
# neutron subnet-create large-priv 171.17.17.0/22 --name large-sub
# neutron router-interface-add ROUTER large-sub

# to delete
# https://docs.openstack.org/ocata/config-reference/compute/config-options.html
# openstack server list -c ID -f value | xargs -n1 openstack server delete
# openstack stack list -c ID -f value | xargs -n1 openstack stack delete

# openstack fixes
# + cpu, mem allocation ratio
# + https://www.ionos.com/community/hosting/mysql/solve-a-mysqlmariadb-too-many-connections-error/
    # mysql -u root -p
    # SET GLOBAL max_connections=1000;
# + Rate limit - https://docs.openstack.org/kilo/config-reference/content/list-of-compute-config-options.html#config_table_nova_api