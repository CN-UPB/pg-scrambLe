# import SonataSchema as sonataSchema
from SonataSchema import NSD, NetworkFunction, ConnectionPoint, VirtualLink, ForwardingGraphs, NetworkForwardingPaths, \
    ConnectionPointsGraph
from collections import OrderedDict
import yaml


class utility():

    def __init__(self):
        self.descriptor_version = ""
        self.vendor = ""
        self.name = ""
        self.version = ""
        self.author = ""
        self.description = ""
        self.list_nf = []
        self.list_connection_points = []
        self.list_virtual_links = []
        self.list_network_forwarding_paths = []
        self.list_connection_points_graph = []
        self.list_forwarding_graphs = []

    def set_general_information(self, source):
        # global descriptor_version
        self.descriptor_version = source['descriptor_version']
        # global vendor
        self.vendor = source['vendor']
        # global name
        self.name = source['name']
        # global version
        self.version = source['version']
        # global author
        self.author = source['author']
        # global description
        self.description = source['description']


    # Function to extract the values "vnf id, vnf vendor, vnf name and vnf version" from Network functions
    def sonata_network_function(self, source):
        network_functions = source

        # network_functions_data = source['network_functions']
        for keyss in network_functions.keys():
            if keyss == 'network_functions':
                network_functions_data = network_functions[keyss]
                # print(network_functions_data)
                for data in network_functions_data:
                    vnf_id = data['vnf_id']
                    vnf_vendor = data['vnf_vendor']
                    vnf_name = data['vnf_name']
                    vnf_version = data['vnf_version']
                    nsd = NetworkFunction(vnf_id, vnf_vendor, vnf_name, vnf_version, [])
                    self.list_nf.append(nsd)
                # print(list_nf)

    # Function to extract the values "id, interface, type" from Connection points
    def sonata_connection_points(self, source):
        connection_points = source
        for keyss in connection_points.keys():
            if keyss == 'connection_points':
                connection_points_data = connection_points[keyss]
                for data in connection_points_data:
                    id = data['id']
                    interface = data['interface']
                    type = data['type']
                    connection_points_instance = ConnectionPoint(id, interface, type)
                    self.list_connection_points.append(connection_points_instance)
                # print(list_connection_points)

    # Function to extract the values "id, connectivity type and connection points reference" from Virtual links
    def virtual_links(self, source):

        virtual_links = source
        for keyss in virtual_links.keys():
            if keyss == 'virtual_links':
                virtual_links_data = virtual_links[keyss]
                for data in virtual_links_data:
                    id = data['id']
                    connectivity_type = data['connectivity_type']
                    connection_points_reference = data['connection_points_reference']
                    virtual_links_instance = VirtualLink(id, connectivity_type, connection_points_reference)
                    self.list_virtual_links.append(virtual_links_instance)
                # print(list_virtual_links)

    # Function to extract the information from "forwarding graph"
    def forwarding_graphs(self, source):
        forwarding_graphs = source
        for keyss in forwarding_graphs.keys():
            if keyss == 'forwarding_graphs':
                forwarding_graphs_data = forwarding_graphs[keyss]
                for data in forwarding_graphs_data:
                    for k in data.keys():
                        if k == "network_forwarding_paths":  # to check if the key matches with "network_forwarding_paths "
                            network_forwarding_paths = data[
                                k]  # extract and save all data present in "network_forwarding_paths"
                            for network_forwarding_paths_data in network_forwarding_paths:
                                for j in network_forwarding_paths_data.keys():
                                    if j == "connection_points":  # check if key matches with "connection_points"
                                        network_forwarding_paths_data1 = network_forwarding_paths_data[
                                            j]  ##extract and save all data present in "connection points"
                                        for connection_points_data in network_forwarding_paths_data1:
                                            connection_point_ref = connection_points_data['connection_point_ref']
                                            position = connection_points_data['position']
                                            connection_points_instance = ConnectionPointsGraph(connection_point_ref,
                                                                                               position)
                                            self.list_connection_points_graph.append(connection_points_instance)
                                            # print(connection_point_ref)
                                fp_id = network_forwarding_paths_data['fp_id']
                                policy = network_forwarding_paths_data['policy']
                                network_forwarding_paths_instance = NetworkForwardingPaths(fp_id, policy,
                                                                                           self.list_connection_points_graph)
                                self.list_network_forwarding_paths.append(network_forwarding_paths_instance)
                                # print(policy)
                        fg_id = data['fg_id']
                        number_of_endpoints = data['number_of_endpoints']
                        number_of_virtual_links = data['number_of_virtual_links']
                        constituent_virtual_links = []
                        if data.get('constituent_virtual_links') is not None:
                            constituent_virtual_links = data['constituent_virtual_links']
                        constituent_vnfs = data['constituent_vnfs']
                        forwarding_graphs_instance = ForwardingGraphs(fg_id, number_of_endpoints,
                                                                      number_of_virtual_links, constituent_vnfs,
                                                                      constituent_virtual_links,
                                                                      self.list_network_forwarding_paths)
                    self.list_forwarding_graphs.append(forwarding_graphs_instance)

    def get_data_sonata(self, received_file_sonata):
        source = received_file_sonata[0]
        self.call_functions(source)

    def call_functions(self, source):
        self.set_general_information(source)
        self.sonata_network_function(source)
        self.sonata_connection_points(source)
        self.virtual_links(source)
        self.forwarding_graphs(source)