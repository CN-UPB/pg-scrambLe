class NsdNsdCatalog:
    nsd = []

    def __init__(self, nsd):
        self.nsd = nsd


class Nsd:
    _id = ""
    name = ""
    short_name = ""
    description = ""
    vendor = ""
    version = "" #optional
    connection_point = []
    logo = "" #optional
    ConstituentVnfd = []
    ConstituentVnfdIndexes = []
    scaling_group_descriptor = []
    vnffgd = []
    vld = []
    ip_profiles = []
    '''Main class representing NSD schema'''
    def __init__(self, _id, name, short_name, description, vendor, version, logo, ConstituentVnfd, vld, connection_point
                 , scaling_group_descriptor, vnffgd):
        self._id = _id
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


class ConnectionPoint:  # class representing connection_points and its properties
    name = ""
    floating_ip_required = ""
    _type = ""

    # optional parameter connection is left
    def __init__(self, name, floating_ip_required, _type):
        self.name = name
        self.floating_ip_required = floating_ip_required
        self._type = _type


class ScalingGroupDescriptor:
    name = ""
    scaling_policy = []
    vnfd_member = []
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


class ScalingConfigAction:  # class representing scaling_config_action properties
    trigger = ""
    ns_service_primitive_name_ref = ""

    def __init__(self, trigger, ns_service_primitive_name_ref):
        self.trigger = trigger
        self.ns_service_primitive_name_ref = ns_service_primitive_name_ref


class Vnffgd:  # class representing forwarding graph and its properties
    _id = ""
    name = ""
    short_name = ""
    vendor = ""
    description = ""
    version = ""
    rsp = []
    classifier = []

    def __init__(self, _id, name, short_name, vendor, description, version, rsp, classifier):
        self._id = _id
        self.name = name
        self.short_name = short_name
        self.vendor = vendor
        self.description = description
        self.version = version
        self.rsp = rsp
        self.classifier = classifier


class Rsp:  # class representing rendered service path
    _id = ""
    name = ""
    vnfd_connection_point_ref = ""
    member_vnf_index_ref = ""
    order = ""
    vnf_id_ref = ""
    vnfd_connection_point_ref = ""

    def __init__(self, _id, name, vnfd_connection_point_ref, member_vnf_index_ref, order, vnf_id_ref):
        self._id = _id
        self.name = name
        self.vnfd_connection_point_ref = vnfd_connection_point_ref
        self.member_vnf_index_ref = member_vnf_index_ref
        self.order = order
        self.vnf_id_ref = vnf_id_ref


class VnfdConnectionPointRefVnffgd:  # class representing vnfd connection point ref property in a forwarding graph
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
    _id = ""
    name = ""
    rsp_id_ref = ""
    match_attributes = []
    member_vnf_index_ref = ""
    vnfd_id_ref = ""
    vnfd_connection_point_ref = ""

    def __init__(self, _id, name, rsp_id_ref, match_attributes, member_vnf_index_ref,
                 vnfd_id_ref, vnfd_connection_point_ref):
        self._id = _id
        self.name = name
        self.rsp_id_ref = rsp_id_ref
        self.match_attributes = match_attributes
        self.member_vnf_index_ref = member_vnf_index_ref
        self.vnfd_id_ref = vnfd_id_ref
        self.vnfd_connection_point_ref = vnfd_connection_point_ref


class MatchAttributes:  # class representing match_attribute property
    _id = ""
    ip_proto = ""
    source_ip_address = ""
    destination_ip_address = ""
    source_port = ""
    destination_port = ""

    def __init__(self, _id, ip_proto, source_ip_address, destination_ip_address, source_port, destination_port):
        self._id = _id
        self.ip_proto = ip_proto
        self.source_ip_address = source_ip_address
        self.destination_ip_address = destination_ip_address
        self.source_port = source_port
        self.destination_port = destination_port


class ConstituentVnfd:  # class representing all virtual network functions
    member_vnf_index = ""
    start_by_default = ""
    vnfd_id_ref = ""

    def __init__(self, member_vnf_index, start_by_default, vnfd_id_ref):
        self.member_vnf_index = member_vnf_index
        self.start_by_default = start_by_default
        self.vnfd_id_ref = vnfd_id_ref


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


class IpProfileParams: #complete
    gateway_address = 0
    ip_version = ""
    subnet_address = ""
    security_group = ""
    dns_server = DnsServer("")
    dhcp_params = DhcpParams("", "", "")
    subnet_prefix_pool = ""

    def __init__(self, ip_version, subnet_address, gateway_address, security_group, dns_server,
                 dhcp_params, subnet_prefix_pool):
        self.gateway_address = gateway_address
        self.ip_version = ip_version
        self.subnet_address = subnet_address
        self.security_group = security_group
        self.dns_server = dns_server
        self.dhcp_params = dhcp_params
        self.subnet_prefix_pool = subnet_prefix_pool


class IpProfiles:
    name = ""
    description = ""
    dns_server = DnsServer("")
    dhcp_params = DhcpParams("", "", "")
    ip_profile_params = IpProfileParams("", "", "", "", dns_server, dhcp_params, "")

    def __init__(self, name, description, ip_profile_params):
        self.name = name
        self.description = description
        self.ip_profile_params = ip_profile_params


class Vld:  # class representing virtual link
    _id = ""
    name = ""
    short_name = ""   # optional
    vendor = ""
    description = ""
    version = ""
    _type = ""
    root_bandwidth = ""
    leaf_bandwidth = ""
    mgmt_network = ""
    vim_network_name = ""  # optional
    ip_profile_ref = ""
    vnfd_connection_point_ref_vld = []

    def __init__(self, _id, name, short_name, vendor, description, version, _type, root_bandwidth, leaf_bandwidth,
                 mgmt_network, vim_network_name, ip_profile_ref, vnfd_connection_point_ref_vld):
        self._id = _id
        self.name = name
        self.short_name = short_name
        self.vendor = vendor
        self.description = description
        self.version = version
        self._type = _type
        self.root_bandwidth = root_bandwidth
        self.leaf_bandwidth = leaf_bandwidth
        self.mgmt_network = mgmt_network
        self.vim_network_name = vim_network_name
        self.ip_profile_ref = ip_profile_ref
        self.vnfd_connection_point_ref_vld = vnfd_connection_point_ref_vld


class VnfdConnectionPointRef:   # class representing vnfd_connection_point_ref property of the schema
    member_vnf_index_ref = ""
    order = "" #
    vnfd_id_ref = ""
    vnfd_connection_point_ref = ""

    def __init__(self, member_vnf_index_ref, order, vnfd_id_ref, vnfd_connection_point_ref):
        self.member_vnf_index_ref = member_vnf_index_ref
        self.order = order
        self.vnfd_id_ref = vnfd_id_ref
        self.vnfd_connection_point_ref = vnfd_connection_point_ref


class VnfDependency:  # class representing VNF dependency property
    vnf_source_ref = ""
    vnf_depends_on_ref = ""

    def __init__(self, vnf_source_ref, vnf_depends_on_ref):
        self.vnf_source_ref = vnf_source_ref
        self.vnf_depends_on_ref = vnf_depends_on_ref

