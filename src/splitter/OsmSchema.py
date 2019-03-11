import yaml
from Fetchfile import Fetchfile


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
    vnfd_connection_point_ref = ""
    member_vnf_index_ref = ""
    order = ""
    vnf_id_ref = ""
    vnfd_connection_point_ref = ""

    def __init__(self, id, name, vnfd_connection_point_ref, member_vnf_index_ref, order, vnf_id_ref):
        self.id = id
        self.name = name
        self.vnfd_connection_point_ref = vnfd_connection_point_ref
        self.member_vnf_index_ref = member_vnf_index_ref
        self.order = order
        self.vnf_id_ref = vnf_id_ref

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
    def __init__(self,id ,name, rsp_id_ref, match_attributes, member_vnf_index_ref, vnfd_id_ref, vnfd_connection_point_ref):
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
    def __init__(self, id, ip_proto, source_ip_address, destination_ip_address, source_port, destination_port):
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