import SonataSchema as sonataSchema
import SonataSchema as sonataSchema
from collections import OrderedDict
import OSM_main as osm_main
import yaml

list_nf = []
list_connection_points = []
list_virtual_links = []
list_network_forwarding_paths = []
list_connection_points_graph = []
list_forwarding_graphs = []


# Function to extract the values "vnf id, vnf vendor, vnf name and vnf version" from Network functions
def sonata_network_function(source):
    network_functions = source[0]

    #network_functions_data = source['network_functions']
    for keyss in network_functions.keys():
        if keyss == 'network_functions':
            network_functions_data = network_functions[keyss]
            print(network_functions_data)
            for data in network_functions_data:
                vnf_id = data['vnf_id']
                vnf_vendor = data['vnf_vendor']
                vnf_name = data['vnf_name']
                vnf_version = data['vnf_version']
                nsd = sonataSchema.NetworkFunction(vnf_id, vnf_vendor, vnf_name, vnf_version, [])
                list_nf.append(nsd)
            #print(list_nf)


# Function to extract the values "id, interface, type" from Connection points
def sonata_connection_points(source):
    connection_points = source[0]
    for keyss in connection_points.keys():
        if keyss == 'connection_points':
            connection_points_data = connection_points[keyss]
            for data in connection_points_data:
                id = data['id']
                interface = data['interface']
                type = data['type']
                connection_points_instance = sonataSchema.ConnectionPoint(id, interface, type)
                list_connection_points.append(connection_points_instance)
            print(list_connection_points)


# Function to extract the values "id, connectivity type and connection points reference" from Virtual links
def virtual_links(source):

    virtual_links = source[0]
    for keyss in virtual_links.keys():
        if keyss == 'virtual_links':
            virtual_links_data = virtual_links[keyss]
            for data in virtual_links_data:
                id = data['id']
                connectivity_type = data['connectivity_type']
                connection_points_reference = data['connection_points_reference']
                virtual_links_instance = sonataSchema.VirtualLink(id, connectivity_type, connection_points_reference)
                list_virtual_links.append(virtual_links_instance)
            print(list_virtual_links)


# Function to extract the information from "forwarding graph"
def forwarding_graphs(source):
    forwarding_graphs = source[0]
    for keyss in forwarding_graphs.keys():
        if keyss == 'forwarding_graphs':
            forwarding_graphs_data = forwarding_graphs[keyss]
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
                                        connection_points_instance = sonataSchema.ConnectionPointsGraph(connection_point_ref,position)
                                        list_connection_points_graph.append(connection_points_instance)
                                        print(connection_point_ref)
                            fp_id = network_forwarding_paths_data['fp_id']
                            policy = network_forwarding_paths_data['policy']
                            network_forwarding_paths_instance = sonataSchema.NetworkForwardingPaths(fp_id, policy, list_connection_points_graph)
                            list_network_forwarding_paths.append(network_forwarding_paths_instance)
                            #print(policy)
                    fg_id = data['fg_id']
                    number_of_endpoints = data['number_of_endpoints']
                    number_of_virtual_links = data['number_of_virtual_links']
                    constituent_virtual_links = data['constituent_virtual_links']
                    constituent_vnfs = data['constituent_vnfs']
                    forwarding_graphs_instance = sonataSchema.ForwardingGraphs(fg_id, number_of_endpoints, number_of_virtual_links, constituent_vnfs, constituent_virtual_links, list_network_forwarding_paths)
                list_forwarding_graphs.append(forwarding_graphs_instance)


def set_general_information(nsd):
    nsd.descriptor_version = source['descriptor_version']
    nsd.vendor = source['vendor']
    nsd.name = source['name']
    nsd.version = source['version']
    nsd.author = source['author']
    nsd.description = source['description']
    return nsd

def get_data_sonata(received_file_sonata):
    source = received_file_sonata
    call_functions(source)

def call_functions(source):
    sonata_network_function(source)
    sonata_connection_points(source)
    virtual_links(source)
    forwarding_graphs(source)
