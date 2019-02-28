import yaml
from Fetchfile import Fetchfile

list_vnfd_connection_point_ref = []
list_vld = []
list_constituent_vnfd = []
list_nsd = []
list_dns_server = []
list_dhcp_params = []
list_connection_point = []
list_scaling_criteria = []
list_scaling_policy = []
list_vnfd_member = []
list_scaling_config_action = []
list_scaling_group_descriptor = []
list_vnfd_connection_point_ref = []
list_rsp = []
list_match_attributes = []
list_classifier = []
list_vnffgd = []
list_vnf_dependency = []
list_ip_profiles = []

def osm_nsd(source):
    print("source is  ")

    #print (source['nsd:nsd-catalog'])
    nsd = source[0]
    #print (nsd)
    for k in nsd.keys():
        if k == "nsd:nsd-catalog":
            nsd_data1 = nsd[k]
            #print(nsd_data1)
            for keyss in nsd_data1.keys():
                #if k == "nsd":
                nsd_data2 = nsd_data1[keyss]
                #print(nsd_data2)
                nsd_data = nsd_data2[0]
                for k1 in nsd_data.keys():
                    if k1 == "connection-point":
                        connection_point = nsd_data[k1]
                        for connection_point_data in connection_point:
                            name = connection_point_data.get('name')
                            floating_ip_required = connection_point_data.get('floating-ip-required')
                            type = connection_point_data.get('type')
                            connection_point_instance = ConnectionPoint(name, floating_ip_required, type)
                            list_connection_point.append(connection_point_instance)
                    elif k1 == "scaling-group-descriptor":
                        scaling_group_descriptor = nsd_data[k1]
                        for scaling_group_descriptor_data in scaling_group_descriptor:
                            for k2 in scaling_group_descriptor_data.keys():
                                if k2 == "scaling-policy":
                                    scaling_policy = scaling_group_descriptor_data[k2]
                                    for scaling_policy_data in scaling_policy:
                                        for k3 in scaling_policy_data.keys():
                                            if k3 == "scaling-criteria":
                                                scaling_criteria = scaling_policy_data[k3]
                                                for scaling_criteria_data in scaling_criteria:
                                                    name = scaling_criteria_data.get('name')
                                                    scale_in_threshold = scaling_criteria_data.get('scale_in_threshold')
                                                    scale_in_relational_operation = scaling_criteria_data.get('scale-in-relational-operation')
                                                    scale_out_threshold = scaling_criteria_data.get('scale_out_threshold')
                                                    scale_out_relational_operation = scaling_criteria_data.get('scale_out_relational_operation')
                                                    ns_monitoring_param_ref = scaling_criteria_data.get('ns_monitoring_param_ref')
                                                    scaling_criteria_instance = ScalingCriteria(name, scale_in_threshold, scale_in_relational_operation, scale_out_threshold, scale_out_relational_operation, ns_monitoring_param_ref)
                                                    list_scaling_criteria.append(scaling_criteria_instance)
                                        name = scaling_policy_data.get('name')
                                        scaling_type = scaling_policy_data.get('scaling_type')
                                        enabled = scaling_policy_data.get('enabled')
                                        scale_in_operation_type = scaling_policy_data.get('scale_in_operation_type')
                                        scale_out_operation_type = scaling_policy_data.get('scale_out_operation_type')
                                        threshold_time = scaling_policy_data.get('threshold_time')
                                        cooldown_time = scaling_policy_data.get('cooldown_time')
                                        scaling_policy_instance = ScalingPolicy(name, scaling_type, enabled, scale_in_operation_type, scale_out_operation_type, threshold_time, cooldown_time, list_scaling_criteria)
                                        list_scaling_policy.append(scaling_policy_instance)
                                elif k2 == "vnfd-member":
                                    vnfd_member = scaling_group_descriptor_data[k2]
                                    for vnfd_member_data in vnfd_member:
                                        min_instance_count = vnfd_member_data.get('min-instance-count')
                                        max_instance_count = vnfd_member_data.get('max-instance-count')
                                        vnfd_member_instance = VnfdMember(min_instance_count, max_instance_count)
                                        list_vnfd_member.append(vnfd_member_instance)
                                elif k2 == "scaling-config-action":
                                    scaling_config_action = scaling_group_descriptor_data[k2]
                                    for scaling_config_action_data in scaling_config_action:
                                        trigger = scaling_config_action_data.get('trigger')
                                        ns_service_primitive_name_ref = scaling_config_action_data.get('ns-service-primitive-name-ref')
                                        scaling_config_action_instance = ScalingConfigAction(trigger, ns_service_primitive_name_ref)
                                        list_scaling_config_action.append(scaling_config_action_instance)
                            name = scaling_group_descriptor_data.get('name')
                            min_instance_count = scaling_group_descriptor_data.get('min_instance_count')
                            max_instance_count = scaling_group_descriptor_data.get('max_instance_count')
                            scaling_group_descriptor_instance = ScalingGroupDescriptor(name, list_scaling_policy, list_vnfd_member, min_instance_count, max_instance_count, list_scaling_config_action)
                            list_scaling_group_descriptor.append(scaling_group_descriptor_instance)
                    elif k1 == "vnffgd":
                        vnffgd = nsd_data[k1]
                        for vnffgd_data in vnffgd:
                            for k2 in vnffgd_data.keys():
                                if k2 == "rsp":
                                    rsp = vnffgd_data[k2]
                                    for rsp_data in rsp:
                                        for k3 in rsp_data.keys():
                                            if k3 == "vnfd-connection-point-ref":
                                                vnfd_connection_point_ref = rsp_data[k3]
                                                for vnfd_connection_point_ref_data in vnfd_connection_point_ref:
                                                    member_vnf_index_ref = vnfd_connection_point_ref_data.get('member_vnf_index_ref')
                                                    order = vnfd_connection_point_ref_data.get('order')
                                                    vnfd_id_ref = vnfd_connection_point_ref_data.get('vnfd_id_ref')
                                                    vnfd_ingress_connection_point_ref = vnfd_connection_point_ref_data.get('vnfd_ingress_connection_point_ref')
                                                    vnfd_egress_connection_point_ref = vnfd_connection_point_ref_data.get('vnfd_egress_connection_point_ref')
                                                    vnfd_connection_point_ref_instance = VnfdConnectionPointRefVnffgd(member_vnf_index_ref, order, vnfd_id_ref, vnfd_ingress_connection_point_ref, vnfd_egress_connection_point_ref)
                                                    list_vnfd_connection_point_ref.append(vnfd_connection_point_ref_instance)
                                        id = rsp_data.get('id')
                                        name = rsp_data.get('name')
                                        rsp_instance = Rsp(id, name, list_vnfd_connection_point_ref)
                                        list_rsp.append(rsp_instance)
                                elif k2 == "classifier":
                                    classifier = vnffgd_data[k2]
                                    for classifier_data in classifier:
                                        for k3 in classifier_data.keys():
                                            if k3 == "match-attributes":
                                                match_attributes = classifier_data[k3]
                                                for match_attributes_data in match_attributes:
                                                    id = match_attributes_data.get('id')
                                                    ip_proto = match_attributes_data.get('ip_proto')
                                                    source_ip_address =match_attributes_data.get('source_ip_address')
                                                    destination_ip_address = match_attributes_data.get('destination_ip_address')
                                                    source_port = match_attributes_data.get('source_port')
                                                    destination_port = match_attributes_data.get('destination_port')
                                                    match_attributes_instance = MatchAttributes(id, ip_proto, source_ip_address, destination_ip_address, source_port, destination_port)
                                                    list_match_attributes.append(match_attributes_instance)
                                        id = classifier_data.get('id')
                                        name = classifier_data.get('name')
                                        rsp_id_ref = classifier_data.get('rsp_id_ref')
                                        member_vnf_index_ref = classifier_data.get('member_vnf_index_ref')
                                        vnfd_id_ref = classifier_data.get('vnfd_id_ref')
                                        vnfd_connection_point_ref = classifier_data.get('vnfd_connection_point_ref')
                                        classifier_instance = Classifier(id, name, rsp_id_ref, list_match_attributes, member_vnf_index_ref, vnfd_id_ref, vnfd_connection_point_ref)
                                        list_classifier.append(classifier_instance)
                            id = vnffgd_data.get('id')
                            name = vnffgd_data.get('name')
                            short_name = vnffgd_data.get('short_name')
                            vendor = vnffgd_data.get('vendor')
                            description = vnffgd_data.get('description')
                            version = vnffgd_data.get('id')
                            vnffgd_instance = Vnffgd(id, name, short_name, vendor, description, version, list_rsp, list_classifier)
                            list_vnffgd.append(vnffgd_instance)


                    elif k1 == "constituent-vnfd":
                        constituent_vnfd = nsd_data[k1]
                        for constituent_vnfd_data in constituent_vnfd:
                            member_vnf_index = constituent_vnfd_data.get('member-vnf-index')
                            vnfd_id_ref = constituent_vnfd_data.get('vnfd-id-ref')
                            start_by_default =constituent_vnfd_data.get('start-by-default')
                            #print(vnfd_id_ref)
                            constituent_vnfd_instance = ConstituentVnfd(member_vnf_index, start_by_default, vnfd_id_ref)
                            list_constituent_vnfd.append(constituent_vnfd_instance)
                            #print(list_constituent_vnfd)
                    elif k1 == "ip-profiles":
                        ip_profiles = nsd_data[k1]
                        for ip_profiles_data in ip_profiles:
                            for k2 in ip_profiles_data.keys():
                                if k2 == "ip-profile-params":
                                    ip_profile_params = ip_profiles_data[k2]
                                    for ip_profile_params_data in ip_profile_params:

                                        print(ip_profile_params_data)
                                        for k3 in ip_profile_params_data.keys():
                                            if k3 == "dns-server":
                                                dns_server = ip_profile_params_data[k3]
                                                for dns_server_data in dns_server:
                                                    address = dns_server_data.get('address')
                                                    dns_server_instance = DnsServer(address)
                                                    list_dns_server.append(dns_server_instance)
                                            elif k3 == "dhcp-params":
                                                dhcp_params = ip_profile_params_data[k3]
                                                for dhcp_params_data in dhcp_params:
                                                    enabled = dhcp_params_data.get('enabled')
                                                    start_address = dhcp_params_data.get('start-address')
                                                    count = dhcp_params_data.get('count')
                                                    print(count)
                                                    dhcp_params_instance = DhcpParams(enabled, start_address, count)
                                                    list_dhcp_params.append(dhcp_params_instance)

                                        gateway_address = ip_profile_params_data.get('gateway-address')
                                        ip_version = ip_profile_params_data.get('ip-version')
                                        subnet_address = ip_profile_params_data.get('subnet-address')
                                        subnet_prefix_pool = ip_profile_params_data.get('subnet-prefix-pool')
                                        security_group = ip_profile_params_data.get('security_group')
                                        ip_profile_params_instance = IpProfileParams(ip_version, subnet_address, gateway_address, security_group, list_dns_server, list_dhcp_params, subnet-prefix-pool)
                            name = ip_profiles_data.get('name')
                            description = ip_profiles_data.get('description')
                            ip_profiles_instance = IpProfiles(name, description, list_dhcp_params)
                            list_ip_profiles.append(ip_profiles_instance)

                    elif k1 =="vnf-dependency":
                        vnf_dependency = nsd_data[k1]
                        for vnf_dependency_data in vnf_dependency:
                            vnf_source_ref = vnf_dependency_data.get('vnf_source_ref')
                            vnf_depends_on_ref = vnf_dependency_data.get('vnf_depends_on_ref')
                            vnf_dependency_instance = VnfDependency(vnf_source_ref, vnf_depends_on_ref)
                            list_vnf_dependency.append(vnf_dependency_instance)



                    elif k1 == "vld":
                        vld = nsd_data[k1]
                        #print(vld)
                        for vld_data in vld:
                            for k2 in vld_data.keys():
                                if k2 == "vnfd-connection-point-ref":
                                    vnfd_connection_point_ref = vld_data[k2]
                                    for vnfd_connection_point_ref_data in vnfd_connection_point_ref:
                                        member_vnf_index_ref = vnfd_connection_point_ref_data.get('member-vnf-index-ref')
                                        order = vnfd_connection_point_ref_data.get('order')
                                        vnfd_id_ref = vnfd_connection_point_ref_data.get('vnfd-id-ref')
                                        vnfd_connection_point_ref = vnfd_connection_point_ref_data.get('vnfd-connection-point-ref')
                                        #print(vnfd_connection_point_ref)
                                        vnfd_connection_point_ref_instance = VnfdConnectionPointRef(member_vnf_index_ref, order, vnfd_id_ref, vnfd_connection_point_ref)
                                        list_vnfd_connection_point_ref.append(vnfd_connection_point_ref_instance)
                                        #print(list_vnfd_connection_point_ref)
                            id = vld_data.get('id')
                            name = vld_data.get('name')
                            short_name = vld_data.get('short-name')
                            vendor = vld_data.get('vendor')
                            description = vld_data.get('description')
                            version = vld_data.get('version')
                            type = vld_data.get('type')
                            root_bandwidth = vld_data.get('root_bandwidth')
                            leaf_bandwidth = vld_data.get('leaf_bandwidth')
                            mgmt_network = vld_data.get('mgmt-network')
                            vim_network_name = vld_data.get('vim-network-name')
                            ip_profile_ref = vld_data.get('ip_profile_ref')
                            print(vim_network_name
                                  )
                            vld_instance = Vld(id, name, short_name, vendor, description, version, type, root_bandwidth, leaf_bandwidth, mgmt_network, vim_network_name, ip_profile_ref, list_vnfd_connection_point_ref)
                            list_vld.append(vld_instance)
                            #print(list_vld)
                id = nsd_data.get('id')
                name = nsd_data.get('name')
                short_name = nsd_data.get('short-name')
                description = nsd_data.get('description')
                vendor = nsd_data.get('vendor')
                logo = nsd_data.get('logo')
                version = nsd_data.get('version')
                nsd_data_instance = Nsd(id, name, short_name, description, vendor, version, logo, list_constituent_vnfd, list_vld, list_connection_point, list_scaling_group_descriptor, list_vnffgd)
                list_nsd.append(nsd_data_instance)
            #print(list_nsd)


class NsdNsdCatalog:
    nsd = []
    def __init__(self, nsd):
        self.nsd = nsd


class Nsd:
    id = ""
    name = ""
    short_name = ""
    description = ""
    vendor = ""
    version = "" #optional
    connection_point = []
    logo = "" #optional
    ConstituentVnfd = []
    scaling_group_descriptor = []
    vnffgd = []
    vld = []
    ip_profiles = []

    def __init__(self,id, name, short_name, description, vendor, version, logo, ConstituentVnfd, vld, connection_point, scaling_group_descriptor, vnffgd):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.description = description
        self.vendor = vendor
        self.version = version
        self.logo = logo
        self.ConstituentVnfd = ConstituentVnfd
        self.vld = vld
        self.connection_point = connection_point
        self.scaling_group_descriptor = scaling_group_descriptor
        self.vnffgd = vnffgd

class ConnectionPoint:
    name = ""
    floating_ip_required = ""
    type = ""
    #optional parameter connection is left
    def __init__(self, name, floating_ip_required, type):
        self.name = name;
        self.floating_ip_required = floating_ip_required
        self.type = type

class ScalingGroupDescriptor:
    name = ""
    scaling_policy = []
    vnfd_member = []  #vnfd-member[member-vnf-index-ref]
    min_instance_count = ""
    max_instance_count = ""
    scaling_config_action = []
    def __init__(self, name, scaling_policy, vnfd_member, min_instance_count, max_instance_count, scaling_config_action):
        self.name = name
        self.scaling_policy = scaling_policy
        self.vnfd_member = vnfd_member
        self.min_instance_count = min_instance_count
        self.max_instance_count = max_instance_count
        self.scaling_config_action = scaling_config_action

class ScalingPolicy:
    name = ""
    scaling_type = ""
    enabled = ""
    scale_in_operation_type = ""
    scale_out_operation_type = ""
    threshold_time = ""
    cooldown_time = ""
    scaling_criteria = []

    def __init__(self, name, scaling_type, enabled, scale_in_operation_type, scale_out_operation_type, threshold_time, cooldown_time, scaling_criteria):
        self.name = name
        self.scaling_type = scaling_type
        self.enabled = enabled
        self.scale_in_operation_type = scale_in_operation_type
        self.scale_out_operation_type = scale_out_operation_type
        self.threshold_time = threshold_time
        self.cooldown_time = cooldown_time
        self.scaling_criteria = scaling_criteria

class ScalingCriteria:
    name = ""
    scale_in_threshold = ""
    scale_in_relational_operation = ""
    scale_out_threshold = ""
    scale_out_relational_operation = ""
    ns_monitoring_param_ref = ""
    def __init__(self, name, scale_in_threshold, scale_in_relational_operation, scale_out_threshold, scale_out_relational_operation, ns_monitoring_param_ref):
        self.name = name
        self.scale_in_threshold = scale_in_threshold
        self.scale_in_relational_operation = scale_in_relational_operation
        self.scale_out_threshold = scale_out_threshold
        self.scale_out_relational_operation = scale_out_relational_operation
        self.ns_monitoring_param_ref = ns_monitoring_param_ref

class VnfdMember:
    member_vnf_index_ref = ""
    count = ""
    def __init__(self, member_vnf_index_ref, count):
        self.member_vnf_index_ref = member_vnf_index_ref
        self.count = count

class ScalingConfigAction:
    trigger = ""
    ns_service_primitive_name_ref = ""
    def __init__(self, trigger, ns_service_primitive_name_ref):
        self.trigger = trigger
        self.ns_service_primitive_name_ref = ns_service_primitive_name_ref

class Vnffgd:
    id = ""
    name = ""
    short_name = ""
    vendor = ""
    description = ""
    version = ""
    rsp = []
    classifier = []
    def __init__(self, id, name, short_name, vendor, description, version, rsp, classifier):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.vendor = vendor
        self.description = description
        self.version = version
        self.rsp = rsp
        self.classifier = classifier

class Rsp:
    id = ""
    name = ""
    vnfd_connection_point_ref = []
    def __init__(self, id, name, vnfd_connection_point_ref):
        self.id = id
        self.name = name
        self.vnfd_connection_point_ref = vnfd_connection_point_ref

class VnfdConnectionPointRefVnffgd:
    member_vnf_index_ref = ""
    order = ""
    vnfd_id_ref = ""
    vnfd_ingress_connection_point_ref = ""
    vnfd_egress_connection_point_ref = ""
    def __init__(self, member_vnf_index_ref, order, vnfd_id_ref, vnfd_ingress_connection_point_ref, vnfd_egress_connection_point_ref):
        self.member_vnf_index_ref = member_vnf_index_ref
        self.order = order
        self.vnfd_id_ref = vnfd_id_ref
        self.vnfd_ingress_connection_point_ref = vnfd_ingress_connection_point_ref
        self.vnfd_egress_connection_point_ref = vnfd_egress_connection_point_ref

class Classifier:
    id = ""
    name = ""
    rsp_id_ref = ""
    match_attributes = []
    member_vnf_index_ref = ""
    vnfd_id_ref = ""
    vnfd_connection_point_ref = ""
    def __init__(self,id ,name, rsp_id_ref, match_attributes, member_vnf_index_ref):
        self.id = id
        self.name = name
        self.rsp_id_ref = rsp_id_ref
        self.match_attributes = match_attributes
        self.member_vnf_index_ref = member_vnf_index_ref
        self.vnfd_id_ref = vnfd_id_ref
        self.vnfd_connection_point_ref = vnfd_connection_point_ref

class MatchAttributes:
    id = ""
    ip_proto = ""
    source_ip_address = ""
    destination_ip_address = ""
    source_port = ""
    destination_port = ""
    def __init__(self, id, ip_proto, source_ip_address, destination_ip_address, destination_port):
        self.id = id
        self.ip_proto = ip_proto
        self.source_ip_address = source_ip_address
        self.destination_ip_address = destination_ip_address
        self.source_port = source_port
        self.destination_port = destination_port



class ConstituentVnfd:  #complete
    member_vnf_index = ""
    start_by_default = ""
    vnfd_id_ref = ""

    def __init__(self, member_vnf_index, start_by_default, vnfd_id_ref):
        self.member_vnf_index = member_vnf_index
        self.start_by_default = start_by_default
        self.vnfd_id_ref = vnfd_id_ref


class IpProfiles:
    name = ""
    description = ""
    ip_profile_params = []
    def __init__(self, name, description, ip_profile_params):
        self.name = name
        self.description = description
        self.ip_profile_params = ip_profile_params


class IpProfileParams: #complete
    gateway_address = 0
    ip_version = ""
    subnet_address = ""
    security_group = ""
    dns_server = []
    dhcp_params = []
    subnet_prefix_pool = ""

    def __init__(self, ip_version, subnet_address, gateway_address, security_group, dns_server, dhcp_params, subnet_prefix_pool):
        self.gateway_address = gateway_address
        self.ip_version = ip_version
        self.subnet_address = subnet_address
        self.security_group = security_group
        self.dns_server = dns_server
        self.dhcp_params = dhcp_params
        self.subnet_prefix_pool = subnet_prefix_pool


class DnsServer:
    address = ""
    def __init__(self, address):
        self.address = address


class DhcpParams:
    enabled = ""
    start_address = ""
    count = ""
    def __init__(self, enabled, start_address, count):
        self.enabled = enabled
        self.start_address = start_address
        self.count = count


class Vld:
    id = ""
    name = ""
    short_name = ""   #optional
    vendor = ""
    description = ""
    version = ""
    type = ""
    root_bandwidth = ""
    leaf_bandwidth = ""
    mgmt_network = ""
    vim_network_name = ""  #optional
    ip_profile_ref = ""
    vnfd_connection_point_ref = []

    def __init__(self, id, name, short_name, vendor, description, version, type, root_bandwidth, leaf_bandwidth, mgmt_network, vim_network_name, ip_profile_ref, vnfd_connection_point_ref):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.vendor = vendor
        self.description = description
        self.version = version
        self.type = type
        self.root_bandwidth = root_bandwidth
        self.leaf_bandwidth = leaf_bandwidth
        self.mgmt_network = mgmt_network
        self.vim_network_name = vim_network_name
        self.ip_profile_ref = ip_profile_ref
        self.vnfd_connection_point_ref = vnfd_connection_point_ref


class VnfdConnectionPointRef:   #complete --- vnfd_connection_point_ref is in 2 names :vnfd_ingress_connection_point_ref and vnfd_egress_connection_point_ref
    member_vnf_index_ref = ""
    order = "" #
    vnfd_id_ref = ""
    vnfd_connection_point_ref = ""

    def __init__(self, member_vnf_index_ref, order, vnfd_id_ref, vnfd_connection_point_ref):
        self.member_vnf_index_ref = member_vnf_index_ref
        self.order = order
        self.vnfd_id_ref = vnfd_id_ref
        self.vnfd_connection_point_ref = vnfd_connection_point_ref

    # def __init__(self, member-vnf-index-ref, vnfd-id-ref, vnfd-connection-point-ref):
    #   self.


class VnfDependency:
    vnf_source_ref = ""
    vnf_depends_on_ref = ""
    def __init__(self, vnf_source_ref, vnf_depends_on_ref):
        self.vnf_source_ref = vnf_source_ref
        self.vnf_depends_on_ref = vnf_depends_on_ref



def get_data(file):
    #with open('D:\Paderborn\project\Implementation\OsmVnfd\hackfest_sfc_ns\hackfest_sfc_nsd.yaml', "r") as incoming_file:
        #data = yaml.load(incoming_file)
        #print(data)
    data = file
    return data

#source = get_data()
#osm_nsd()