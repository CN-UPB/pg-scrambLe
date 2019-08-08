{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf400
{\fonttbl\f0\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\csgray\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww28020\viewh8400\viewkind0
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0

\f0\fs28 \cf2 \CocoaLigature0 echo -n "Enter project name > "\
read project\
echo -n "Enter the value of x in 192.168.x.0/24 subnet-range for creating the subnet >"\
read x\
openstack project create --description "Project for $project" --enable $project\
openstack user create --project $project --password "1234" --description "User for project $project" --enable $project-user\
openstack role add --project $project --user $project-user admin\
openstack quota set --instances 10000 --server-groups 100000 --ram 51200000 --key-pairs 100000 --fixed-ips 50000 --injected-file-size 10240000 --server-group-members 10000 --injected-files 5000 --cores 20000 --injected-path-size 255000 --per-volume-gigabytes 10000 --gigabytes 1000000 --backup-gigabytes 1000000 --snapshots 10000 --volumes 10000 --backups 10000 --subnetpools 10000 --vips 10000 --ports 50000 --subnets 10000 --networks 10000 --floating-ips 50000 --secgroup-rules 100000 --secgroups 10000 --routers 10000 --rbac-policies 10000 $project\
openstack network create $project-priv\
openstack subnet create $project-priv-sub --network $project-priv --subnet-range 192.168.$x.0/24\
openstack router create --project $project $project-router\
openstack router set $project-router --external-gateway public\
openstack router add subnet $project-router $project-priv-sub}