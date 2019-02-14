class Vld:
    id = ""
    name = ""
    type = ""
    mgmt_network = ""
    vim_network_name = ""
    vnfd_connection_point_ref = []

    def __init__(self, id, name, type, mgmt_network, vim_network_name, vnfd_connection_point_ref):
        self.id = id
        self.name = name
        self.type = type
        self.mgmt_network = mgmt_network
        self.vim_network_name = vim_network_name
        self.vnfd_connection_point_ref = vnfd_connection_point_ref


class VnfdConnectionPointRef:
    member_vnf_index_ref = ""
    vnfd_id_ref = ""
    vnfd_connection_point_ref = ""

    def __init__(self, member_vnf_index_ref, vnfd_id_ref, vnfd_connection_point_ref):
        self.member_vnf_index_ref = member_vnf_index_ref
        self.vnfd_id_ref = vnfd_id_ref
        self.vnfd_connection_point_ref = vnfd_connection_point_ref

    # def __init__(self, member-vnf-index-ref, vnfd-id-ref, vnfd-connection-point-ref):
    #   self.

class ConstituentVnfd:
    member_vnf_index = ""
    start_by_default = ""
    vnfd_id_ref = ""

    def __init__(self, member_vnf_index, start_by_default, vnfd_id_ref):
        self.member_vnf_index = member_vnf_index
        self.start_by_default = start_by_default
        self.vnfd_id_ref = vnfd_id_ref


class Nsd:
    ConstituentVnfd = []
    id = ""
    name = ""
    short_name = ""
    description = ""
    vendor = ""
    vld = []

    def __init__(self,ConstituentVnfd,id, name, short_name, description, vendor, vld):
        self.id = id
        self.ConstituentVnfd = ConstituentVnfd
        self.name = name
        self.short_name = short_name
        self.description = description
        self.vendor = vendor
        self.vld = vld
