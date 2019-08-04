../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N cirros_ns/cirros_vnf_vnfd
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N cirros_ns/cirros_case1_nsd/
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N cirros_ns/cirros_case2_nsd/
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N cirros_ns/cirros_case3_nsd/

# old stress image
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N stress_ns/stress_vnf_vnfd
# ../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N stress_auto_vnf_vnfd
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N stress_ns/stress_case1_nsd/
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N stress_ns/stress_case3_nsd/
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N stress_ns/stress_case2_nsd/

../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t vnfd -N ubuntu_ns/ubuntu_vnf_vnfd
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N ubuntu_ns/ubuntu_case1_nsd/
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N ubuntu_ns/ubuntu_case2_nsd/
../devops/descriptor-packages/tools/generate_descriptor_pkg.sh -t nsd -N ubuntu_ns/ubuntu_case3_nsd/
