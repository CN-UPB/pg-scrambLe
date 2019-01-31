class GeneralInformation:
    descriptor_version = ""
    vendor = ""
    name = ""
    version = ""
    author = ""
    description = ""


class VirtualFunction:
    vnf_id = ""
    vnf_name = ""
    vnf_vendor = ""
    connection_point_refs = []

    def __init__(self, vnf_id, vnf_vendor, vnf_name, connection_point_refs):
        self.vnf_id = vnf_id
        self.vnf_vendor = vnf_vendor
        self.vnf_name = vnf_name
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
