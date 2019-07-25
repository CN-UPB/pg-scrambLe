import SonataSchema


class Utility:
    
    def __init__(self, source):
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

        '''Call utility functions one after another.'''
        self.set_general_information(source)
        self.sonata_network_function(source)
        self.sonata_connection_points(source)
        self.virtual_links(source)
        self.forwarding_graphs(source)

    '''Sets the general information (version, vendor, name, author, description) specific to the NSD'''
    def set_general_information(self, source):
        try:
            self.descriptor_version = source['descriptor_version']
            self.vendor = source['vendor']
            self.name = source['name']
            self.version = source['version']
            self.author = source['author']
            self.description = source['description']
        except KeyError:
            print("One or many keys not found!")

    '''Function to extract the values "vnf id, vnf vendor, vnf name and vnf version" from Network functions'''
    def sonata_network_function(self, source):
        network_functions = source
        try:
            for key in network_functions.keys():
                if key == 'network_functions':
                    network_functions_data = network_functions[key]
                    for data in network_functions_data:
                        vnf_id = data['vnf_id']
                        vnf_vendor = data['vnf_vendor']
                        vnf_name = data['vnf_name']
                        vnf_version = data['vnf_version']
                        nsd = SonataSchema.NetworkFunction(vnf_id, vnf_vendor, vnf_name, vnf_version, [])
                        self.list_nf.append(nsd)
        except KeyError:
            print("One or many keys not found!")

    '''Function to extract the values "id, interface, type" from Connection points'''
    def sonata_connection_points(self, source):
        connection_points = source
        try:
            for key in connection_points.keys():
                if key == 'connection_points':
                    connection_points_data = connection_points[key]
                    for data in connection_points_data:
                        _id = data['id']
                        interface = data['interface']
                        _type = data['type']
                        connection_points_instance = SonataSchema.ConnectionPoint(_id, interface, _type)
                        self.list_connection_points.append(connection_points_instance)
        except KeyError:
            print("One or many keys not found!")

    '''Function to extract the values "id, connectivity type and connection points reference" from Virtual links'''
    def virtual_links(self, source):
        virtual_links = source
        try:
            for key in virtual_links.keys():
                if key == 'virtual_links':
                    virtual_links_data = virtual_links[key]
                    for data in virtual_links_data:
                        _id = data['id']
                        connectivity_type = data['connectivity_type']
                        connection_points_reference = data['connection_points_reference']
                        virtual_links_instance = SonataSchema.VirtualLink(_id, connectivity_type, connection_points_reference)
                        self.list_virtual_links.append(virtual_links_instance)
        except KeyError:
            print("One or many keys not found!")

    '''Function to extract the information from "forwarding graph"'''
    def forwarding_graphs(self, source):
        forwarding_graphs = source
        try:
            for key in forwarding_graphs.keys():
                if key == 'forwarding_graphs':
                    forwarding_graphs_data = forwarding_graphs[key]
                    for data in forwarding_graphs_data:
                        for k in data.keys():
                            # to check if the key matches with "network_forwarding_paths "
                            if k == "network_forwarding_paths":
                                # extract and save all data present in "network_forwarding_paths"
                                network_forwarding_paths = data[k]
                                for network_forwarding_paths_data in network_forwarding_paths:
                                    for j in network_forwarding_paths_data.keys():
                                        # check if key matches with "connection_points"
                                        if j == "connection_points":
                                            # extract and save all data present in "connection points"
                                            network_forwarding_paths_data1 = network_forwarding_paths_data[j]
                                            for connection_points_data in network_forwarding_paths_data1:
                                                connection_point_ref = connection_points_data['connection_point_ref']
                                                position = connection_points_data['position']
                                                connection_points_instance = SonataSchema.ConnectionPointsGraph(connection_point_ref,
                                                                                                   position)
                                                self.list_connection_points_graph.append(connection_points_instance)

                                    fp_id = network_forwarding_paths_data['fp_id']
                                    policy = network_forwarding_paths_data['policy']
                                    network_forwarding_paths_instance = SonataSchema.NetworkForwardingPaths(
                                        fp_id, policy, self.list_connection_points_graph)
                                    self.list_network_forwarding_paths.append(network_forwarding_paths_instance)

                            fg_id = data['fg_id']
                            number_of_endpoints = data['number_of_endpoints']
                            number_of_virtual_links = data['number_of_virtual_links']
                            constituent_virtual_links = []
                            if data.get('constituent_virtual_links') is not None:
                                constituent_virtual_links = data['constituent_virtual_links']
                            constituent_vnfs = data['constituent_vnfs']
                            forwarding_graphs_instance = SonataSchema.ForwardingGraphs(fg_id, number_of_endpoints,
                                                                          number_of_virtual_links, constituent_vnfs,
                                                                          constituent_virtual_links,
                                                                          self.list_network_forwarding_paths)
                        self.list_forwarding_graphs.append(forwarding_graphs_instance)
        except KeyError:
            print("One or many keys not found!")
