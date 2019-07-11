class NSD:  # class representing overall NSD and its properties
    descriptor_version = ""  # variable representing version of the descriptor
    vendor = ""  # vendor name
    name = ""  # name of the descriptor
    version = ""
    author = ""  # author of the descriptor
    description = ""  # a short description about the descriptor
    networkFunctions = []  # list of network functions
    connectionPoints = []  # list of connection points
    virtualLinks = []  # set of virtual links connecting virtual functions
    forwardingGraphs = []  # set of forwarding graphs

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


class NetworkFunction:  # class representing a network function and its properties
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


class ConnectionPoint:  # class representing a connection point and its properties
    _id = ""
    interface = ""
    _type = ""

    def __init__(self, _id, interface, _type):
        self._id = _id
        self.interface = interface
        self._type = _type


class VirtualLink:  # class representing a virtual link and its properties
    _id = ""
    # connectivity type can be 'E-LAN' representing many to many connectivity or
    # 'E-Line' representing one to one
    connectivity_type = ""
    connection_points_reference = []

    def __init__(self, _id, connectivity_type, connection_points_reference):
        self._id = _id
        self.connectivity_type = connectivity_type
        self.connection_points_reference = connection_points_reference


class ForwardingGraphs:  # class representing a forwarding graph and its properties
    fg_id = ""
    number_of_endpoints = 0
    number_of_virtual_links = 0
    constituent_virtual_links = []
    constituent_vnfs = []  # represents set of virtual functions making this graph
    network_forwarding_path = []

    def __init__(self, fg_id, number_of_endpoints, number_of_virtual_links, constituent_vnfs,
                 constituent_virtual_links, network_forwarding_path):
        self.fg_id = fg_id
        self.number_of_endpoints = number_of_endpoints
        self.number_of_virtual_links = number_of_virtual_links
        self.constituent_vnfs = constituent_vnfs
        self.constituent_virtual_links = constituent_virtual_links
        self.network_forwarding_path = network_forwarding_path


class NetworkForwardingPaths:  # class representing a network forwarding path and its properties
    fp_id = ""
    policy = ""
    connection_points = []

    def __init__(self, fp_id, policy, connection_points):
        self.fp_id = fp_id
        self.policy = policy
        self.connection_points = connection_points


class ConnectionPointsGraph:  # class representing a connection point of a forwarding graph and its properties
    connection_point_ref = ""
    position = 0  # represents the position of the connection point

    def __init__(self, connection_point_ref, position):
        self.connection_point_ref = connection_point_ref
        self.position = position
