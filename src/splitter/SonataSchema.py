list_nf = []
list_connection_points = []
list_virtual_links = []
list_network_forwarding_paths = []
list_connection_points_graph = []
list_forwarding_graphs = []

# Function to extract the values "vnf id, vnf vendor, vnf name and vnf version" from Network functions

def sonata_network_function():
    network_functions_data = source['network_functions']
    for data in network_functions_data:
        vnf_id = data['vnf_id']
        vnf_vendor = data['vnf_vendor']
        vnf_name = data['vnf_name']
        vnf_version = data['vnf_version']
        nsd = NetworkFunction(vnf_id, vnf_vendor, vnf_name, vnf_version)
        list_nf.append(nsd)
        #print(list_nf)

# Function to extract the values "id, interface, type" from Connection points

def sonata_connection_points():
    connection_points_data = source['connection_points']
    for data in connection_points_data:
        id = data['id']
        interface = data['interface']
        type = data['type']
        connection_points_instance = ConnectionPoints(id, interface, type)
        list_connection_points.append(connection_points_instance)
        #print(list_connection_points)

# Function to extract the values "id, connectivity type and connection points reference" from Virtual links

def virtual_links():
    virtual_links_data = source['virtual_links']
    for data in virtual_links_data:
        id = data['id']
        connectivity_type = data['connectivity_type']
        connection_points_reference = data['connection_points_reference']
        virtual_links_instance = VirtualLinks(id, connectivity_type, connection_points_reference)
        list_virtual_links.append(virtual_links_instance)
        #print(connection_points_reference)

# Function to extract the information from "forwarding graph"

def forwarding_graphs():
    forwarding_graphs_data = source['forwarding_graphs']
    for data in forwarding_graphs_data:
        for k in data.keys():
            if k == "network_forwarding_paths":    #to check if the key matches with "network_forwarding_paths "
                network_forwarding_paths = data[k]  #extract and save all data present in "network_forwarding_paths"
                for network_forwarding_paths_data in network_forwarding_paths:
                    for j in network_forwarding_paths_data.keys():
                        if j == "connection_points":   #check if key matches with "connection_points"
                            network_forwarding_paths_data1 = network_forwarding_paths_data[j] ##extract and save all data present in "connection points"
                            for connection_points_data in network_forwarding_paths_data1:
                                connection_point_ref = connection_points_data['connection_point_ref']
                                position = connection_points_data['position']
                                connection_points_instance = ConnectionPointsGraph(connection_point_ref,position)
                                list_connection_points_graph.append(connection_points_instance)
                                print(connection_point_ref)
                    fp_id = network_forwarding_paths_data['fp_id']
                    policy = network_forwarding_paths_data['policy']
                    network_forwarding_paths_instance = NetworkForwardingPaths(fp_id, policy, list_connection_points_graph)
                    list_network_forwarding_paths.append(network_forwarding_paths_instance)
                    print(policy)
            fg_id = data['fg_id']
            number_of_endpoints = data['number_of_endpoints']
            number_of_virtual_links = data['number_of_virtual_links']
            constituent_virtual_links = data['constituent_virtual_links']
            constituent_vnfs = data['constituent_vnfs']
            forwarding_graphs_instance = ForwardingGraphs(fg_id, number_of_endpoints, number_of_virtual_links, constituent_virtual_links, constituent_vnfs, list_network_forwarding_paths)
            list_forwarding_graphs.append(forwarding_graphs_instance)
        #print(number_of_virtual_links)


class GeneralInformation:
    descriptor_version = ""
    vendor = ""
    name = ""
    version = ""
    author = ""
    description = ""


class NetworkFunctions:
    vnf_id = ""
    vnf_name = ""
    vnf_vendor = ""
    connection_point_refs = []

    def __init__(self, vnf_id, vnf_vendor, vnf_name, connection_point_refs):
        self.vnf_id = vnf_id
        self.vnf_vendor = vnf_vendor
        self.vnf_name = vnf_name
        self.connection_point_refs = connection_point_refs


class ConnectionPoints:
    id = ""
    interface = ""
    type = ""

    def __init__(self, id, interface, type):
        self.id = id
        self.interface = interface
        self.type = type


class VirtualLinks:
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

    def __init__(self, fg_id, number_of_endpoints, number_of_virtual_links, constituent_vnfs, network_forwarding_path):
        self.fg_id = fg_id
        self.number_of_endpoints = number_of_endpoints
        self.number_of_virtual_links = number_of_virtual_links
        self.constituent_vnfs = constituent_vnfs
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

#with open("D:\Paderborn\project\Implementation\sonata-demo.yml", "r") as incoming_file:
    #source = yaml.load(incoming_file)
    sonata_network_function()
    sonata_connection_points()
    virtual_links()
    forwarding_graphs()