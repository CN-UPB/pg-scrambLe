./devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N scramble_client_vnf/
./devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N scramble_tcpdump_vnf/
./devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N scramble_haproxy_vnf/
./devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N scramble_nginx_1_vnf/
./devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N scramble_nginx_2_vnf/
./devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N scramble_3vnf_load_balancer_nsd/

python osm_helper.py vnf="/home/ashwin/Documents/MSc/pg-scramble/pg-scramble/doc/Adaptor/ScalabilityResearch/Loadbalancing-NS/OSM-Descriptors/scramble_client_vnf.tar.gz"