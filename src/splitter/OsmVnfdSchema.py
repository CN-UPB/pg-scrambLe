class Vnfd:
    descriptor_version = ""
    vendor = ""
    name = ""
    version = ""
    author = ""
    description = ""
    function_specific_managers = []
    virtual_deployment_units = []
    virtual_links = []
    connection_points = []
    monitoring_rules = []


    def __init__(self, descriptor_version, vendor, name, version, author, description, function_specific_managers, virtual_deployment_units, virtual_links, connection_points, monitoring_rules):
        self.descriptor_version = descriptor_version
        self.vendor = vendor
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.function_specific_managers = function_specific_managers
        self.virtual_deployment_units = virtual_deployment_units
        self.virtual_links = virtual_links
        self.connection_points = connection_points
        self.monitoring_rules = monitoring_rules


class function_specific_managers:
    id = ""
    description = ""
    image = ""
    options = []
    resource_requirements = []

    def __init__(self, id, description, image, options, resource_requirements):
        self.id = id
        self.description = description
        self.image = image
        self.options = options
        self.resource_requirements = resource_requirements


class virtual_deployment_units:
    id = ""
    vm_image = ""
    vm_image_format = ""
    resource_requirements = []
    memory = []
    storage = []
    monitoring_parameters = []
    connection_points = []

    def __init__(self, id, vm_image, vm_image_format, resource_requirements, memory, storage, monitoring_parameters, connection_points):
        self.id = id
        self.vm_image = vm_image
        self.vm_image_format = vm_image_format
        self.resource_requirements = resource_requirements
        self.memory = memory
        self.storage = storage
        self.monitoring_parameters = monitoring_parameters
        self.connection_points = connection_points



class ResourceRequirements:
    cpu = []
    def __init__(self, cpu):
        self.cpu = cpu

class memory:
    size = 0
    size_unit = ""
    def __init__(self, size, size_unit):
        self.size = size_unit
        self.size_unit = size_unit

class Storage:
    size = 0
    size_unit = ""
    def __init__(self, size, size_unit):
        self.seze = size
        self.size_unit = size_unit

class MonitoringParameters:
    name = ""
    unit = ""
    def __init__(self, name):
        self.name = name
        self.unit = unit

class ConnectionPoints:
    id = ""
    interface = ""
    type = ""
    def __init__(self, interface, type):
        self.interface = interface
        self.type = type

#The VNF connection points to the outside world.
class VnfConnectionPoints:
    id = ""
    interface = ""
    type = ""
    def __init__(self, id, interface, type):
        self.id = id
        self.interface = interface
        self.type = interface

class VirtualLinks:
    id = ""
    connectivity_type = ""
    connection_points_reference = ""
    dhcp = ""
    def __init__(self, id, connectivity_type, connection_points_reference, dhcp):
        self.id = id
        self.connectivity_type = connectivity_type
        self.connection_points_reference = connection_points_reference
        self.dhcp = dhcp

class MonitoringRules:
    name = ""
    description = ""
    duration = ""
    duration_unit = ""
    condition = ""
    notification = []

    def __init__(self, name, description, duration, duration_unit, condition, notification):
        self.name = name
        self.description = description
        self.duration = duration
        self.duration_unit = duration_unit
        self.condition = condition
        self.notification = notification

class Notification:
    name =""
    type =""
    def __init__(self, name, type):
        self.name = name
        self.type = type












