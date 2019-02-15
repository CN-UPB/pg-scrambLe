class MainVnfd:
    vnfd = []
    def __init__(self,vnfd):
        self.vnfd = vnfd

class Vnfd:
    id = ""
    name = ""
    short_name = ""
    description = ""
    vendor = ""
    logo = ""
    version = ""
    connection_point = []
    internal_vld = [] #optional
    mgmt_interface = []
    vdu = []
    vnf_configuration = []

    def __init__(self, id, name, short_name, description, vendor, logo, version, connection_point, internal_vld , mgmt_interface,  vdu, vnf_configuration):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.description = description
        self.vendor = vendor
        self.logo = logo
        self.version = version
        self.connection_point = connection_point
        self.internal_vld = internal_vld
        self.mgmt_interface = mgmt_interface
        self.vdu = vdu
        self.vnf_configuration = vnf_configuration

class ConnectionPoint:
    id = ""  #optional
    name = ""
    short_name = ""
    type = ""
    def __init__(self, name, type, id,  short_name):
        self.name = name
        self.type = type
        self.id = id
        self.short_name = short_name

class InternalVld:
    id = ""
    name = ""
    short_name = ""
    type = ""
    internal_connection_point = []
    def __init__(self, id, name, short_name, type, internal_connection_point):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.type = type
        self.internal_connection_point = internal_connection_point
class InternalConnectionPoint:
    id_ref = ""
    id_ref1 = ""
    def __init__(self, id_ref, id_ref1):
        self.id_ref = id_ref
        self.id_ref1 = id_ref




class MgmtInterface:
    cp = ""
    def __init__(self, cp):
        self.cp = cp

class Vdu:
    id = ""
    name = ""
    description = "" #optional
    count = 0
    vm_flavor = []
    guest_epa = []
    image = ""
    interface = []
    internal_connection_point = []
    cloud_init_file = ""
    def __init__(self, id, name, description, count, vm_flavor, guest_epa, image, interface, cloud_init_file):
        self.id = id
        self.name = name
        self.description = description
        self.count = count
        self.vm_flavor = vm_flavor
        self.guest_epa = guest_epa
        self.image = image
        self.interface = interface
        self.cloud_init_file = cloud_init_file


class Vmflavor:
    vcpu_count = 0
    memory_mb = 0
    storage_gb = 0
    def __init__(self, vcpu_count, memory_mb, storage_gb):
        self.vcpu_count = vcpu_count
        self.memory_mb = memory_mb
        self.storage_gb = storage_gb

class GuestEpa:
    cpu_pinning_policy = ""
    cpu_thread_pinning_policy = ""
    mempage_size = ""
    numa_node_policy = []
    def __init__(self, cpu_pinning_policy, cpu_thread_pinning_policy, mempage_size, numa_node_policy):
        self.cpu_pinning_policy = cpu_pinning_policy
        self.cpu_thread_pinning_policy = cpu_thread_pinning_policy
        self.mempage_size = mempage_size
        self.numa_node_policy = numa_node_policy

class Numa_node_policy:
    mem_policy = ""
    node_cnt = ""
    node = []
    def __init__(self, mem_policy, node_cnt, node):
        self.mem_policy = mem_policy
        self.node_cnt = node_cnt
        self.node = node

class node:
    id = ""
    def __init__(self, id):
        self.id = id


class Interface:
    name = ""
    position = ""
    type = ""
    virtual_interface = []
    external_connection_point_ref = ""

    def __init__(self, name, position,  type, virtual_interface, external_connection_point_ref):
        self.name = name
        self.position = position
        self.type = type
        self.virtual_interface = virtual_interface
        self.external_connection_point_ref = external_connection_point_ref

class InternalConnectionPoint:
    id = ""
    name = ""
    short_name = ""
    type = ""
    def __init__(self, id, name, short_name):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.type = type


class Virtualnterface:
    type = ""
    bandwidth = "" #optional
    vpci = "" #optional
    def __init__(self, type, bandwidth, vpci):
        self.type = type
        self.bandwidth = bandwidth
        self.vpci = vpci


class VnfConfiguration:
    juju = []
    initial_config_primitive = []
    config_primitive = []
    def __init__(self, juju, initial_config_primitive, config_primitive):
        self.juju = juju
        self.initial_config_primitive = initial_config_primitive
        self.config_primitive = config_primitive

class Juju:
    charm = ""
    def __init__(self, charm):
        self.charm = charm

class InitialConfigPrimitive:
    seq = 0
    name = ""
    parameter = []
    def __init__(self, seq, name, parameter):
        self.seq = seq
        self.name = name
        self.parameter = parameter

class Parameter:
    name = ""
    value = ""
    def __init__(self, name, value):
        self.name = name
        self.value = value

class ConfigPrimitive:
    name = ""
    parameter = []
    def __init__(self, name, parameter):
        self.name = name
        self.parameter = parameter
class Parameter:
    name = ""
    data_type = ""
    mandatory = ""
    def __init__(self, name, data_type, mandatory):
        self.name = name
        self.data_type = data_type
        self.mandatory = mandatory








