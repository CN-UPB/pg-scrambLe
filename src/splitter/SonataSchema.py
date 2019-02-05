class NSD:
    descriptor_version = ""
    vendor = ""
    name = ""
    version = ""
    author = ""
    description = ""
    networkFunctions = []
    connectionPoints = []
    virtualLinks = []
    forwardingGraphs = []

    def __init__(self, descriptor_version, vendor, name, version, author, description, network_functions,
                 connection_points, virtual_links, forwarding_graphs):
        self.descriptor_version = descriptor_version
        self.vendor = vendor
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.networkFunctions = network_functions
        self.connectionPoints = connection_points
        self.virtualLinks = virtual_links
        self.forwardingGraphs = forwarding_graphs


class NetworkFunction:
    vnf_id = ""
    vnf_name = ""
    vnf_vendor = ""
    vnf_version = ""
    connection_point_refs = []

    def __init__(self, vnf_id, vnf_vendor, vnf_name, vnf_version, connection_point_refs):
        self.vnf_id = vnf_id
        self.vnf_vendor = vnf_vendor
        self.vnf_name = vnf_name
        self.vnf_version = vnf_version
        self.connection_point_refs = connection_point_refs


class ConnectionPoint:
    id = ""
    interface = ""
    type = ""

    def __init__(self, id, interface, type):
        self.id = id
        self.interface = interface
        self.type = type


class VirtualLink:
    id = ""
    connectivity_type = ""
    connection_points_reference = []

    def __init__(self, id, connectivity_type, connection_points_reference):
        self.id = id
        self.connectivity_type = connectivity_type
        self.connection_points_reference = connection_points_reference


class ForwardingGraphs:
    fg_id = ""
    number_of_endpoints = 0
    number_of_virtual_links = 0
    constituent_virtual_links = []
    constituent_vnfs = []
    network_forwarding_path = []

    def __init__(self, fg_id, number_of_endpoints, number_of_virtual_links, constituent_vnfs, constituent_virtual_links, network_forwarding_path):
        self.fg_id = fg_id
        self.number_of_endpoints = number_of_endpoints
        self.number_of_virtual_links = number_of_virtual_links
        self.constituent_vnfs = constituent_vnfs
        self.constituent_virtual_links = constituent_virtual_links
        self.network_forwarding_path = network_forwarding_path


class NetworkForwardingPaths:
    fp_id = ""
    policy = ""
    connection_points = []

    def __init__(self, fp_id, policy, connection_points):
        self.fp_id = fp_id
        self.policy = policy
        self.connection_points = connection_points


class ConnectionPointsGraph:
    connection_point_ref = ""
    position = 0

    def __init__(self, connection_point_ref, position):
        self.connection_point_ref = connection_point_ref
        self.position = position

