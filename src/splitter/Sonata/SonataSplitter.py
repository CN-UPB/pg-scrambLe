import logging
import Sonata.SonataSchema as SonataSchema 

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("scramble:splitter")


class splitter():

    def __init__(self, vnf_sets, utility=None):
        self.utilityFunctions = utility
        self.NSDs = []
        self.network_function_sets = vnf_sets
        self.old_new_link_mapping = []
        self.processed_connection_point_path = []

    """
    Validates the network function sets. It checks for following things
    - No invalid VNF is provided in the input set.
    - Number of virtual functions provided in the input set matches with the no. of VNFs in the NSD.
    """
    def validate(self):
        size = 0
        list_network_function = []
        for network_function_set in self.network_function_sets:
            size = size + len(network_function_set)
            for network_function in network_function_set:
                list_network_function.append(network_function)

        if size != len(self.utilityFunctions.list_nf):
            return False
        if len(list_network_function) != len(set(list_network_function)):
            return False

    """
    Takes virtual function name as an argument and returns the complete vnf object with all properties
    """
    def get_network_function_object(self, vnf_name):
        for nf_object in self.utilityFunctions.list_nf:
            if nf_object.vnf_id == vnf_name:
                return nf_object
        return None

    """
    Takes connection point id as an argument and returns the type of connection point i.e. External or Management,
    else returns not_external if connection point id provided is invalid.
    """
    # returns type of connection point (external, management)
    def get_connection_point_type(self, connection_point_id):
        for connection_point in self.utilityFunctions.list_connection_points:
            if connection_point._id == connection_point_id:
                return connection_point._type
        return "not_external"

    """
    This method splits the set of network functions, and creates an empty NSD class object.
    """
    def split_network_function(self):
        for network_function_set in self.network_function_sets:
            sub_nsd = SonataSchema.NSD("", "", "", "", "", "", [], [], [], [])
            network_function_list = []
            for network_function in network_function_set:
                network_function_list.append(self.get_network_function_object(network_function))
                sub_nsd.networkFunctions = network_function_list
            self.NSDs.append(sub_nsd)
            
    """
    This method gets all the internal links with connectivity type representing one to one connection i.e. E-Line
    """
    def get_internal_links(self):
        internal_links = []
        for virtual_link in self.utilityFunctions.list_virtual_links:
            if virtual_link.connectivity_type == "E-Line":
                internal_link = []
                cp_0 = virtual_link.connection_points_reference[0]
                cp_1 = virtual_link.connection_points_reference[1]
                if self.get_connection_point_type(cp_0) != "external" and \
                        self.get_connection_point_type(cp_1) != "external":
                    vnf_1 = cp_0.split(":")
                    vnf_2 = cp_1.split(":")
                    internal_link.append(vnf_1[0])
                    internal_link.append(vnf_2[0])
                    internal_links.append(internal_link)
        return internal_links

    """
    This method creates a new function set if the network function to be splitted is pulled out of sequence.
    For example. if VNF_1, VNF_2, VNF_3 are is the set and VNF_2 is pulled out then we will create three sets each
    having single VNF.
    """
    # creates new function sets if needed
    def create_new_function_sets(self):
        changed = 0
        for network_function_set in self.network_function_sets:
            if len(network_function_set) == 2:
                if network_function_set not in self.get_internal_links() and \
                        network_function_set[::-1] not in self.get_internal_links():
                    for network_function in network_function_set:
                        new_sub_network_function_set = []
                        new_sub_network_function_set.append(network_function)
                        self.new_network_function_set.append(new_sub_network_function_set)
                        changed = 1
            if len(network_function_set) == 1 and changed == 1:
                self.new_network_function_set.append(network_function_set)
            if changed == 1:
                self.network_function_sets = self.new_network_function_set

    """
    This method loads the connection points into the empty NSD objects.
    """
    def set_connection_points(self):
        for i in range(len(self.network_function_sets)):
            nsd_cp = self.NSDs[i]
            nsd_cp.connectionPoints = self.utilityFunctions.list_connection_points
            self.NSDs[i] = nsd_cp

    """
    Method sets the following general information common to all sub NSDs
    - descriptor version
    - vendor
    - name
    - version
    - author
    - description
    """
    def set_general_information(self):
        for i in range(len(self.network_function_sets)):
            nsd_general_info = self.NSDs[i]
            nsd_general_info.descriptor_version = self.utilityFunctions.descriptor_version
            nsd_general_info.vendor = self.utilityFunctions.vendor
            nsd_general_info.name = self.utilityFunctions.name
            nsd_general_info.version = self.utilityFunctions.version
            nsd_general_info.author = self.utilityFunctions.author
            nsd_general_info.description = self.utilityFunctions.description
            self.NSDs[i] = nsd_general_info

    """
    This method sets the connection point refs for the virtual functions
    """
    def set_connection_point_refs_for_virtual_functions(self):
        for virtual_link in self.utilityFunctions.list_virtual_links:
            for connection_point_ref in virtual_link.connection_points_reference:
                split_string = connection_point_ref.split(':')
                if self.get_network_function_object(split_string[0]) is not None:
                    self.get_network_function_object(split_string[0]).connection_point_refs.append(
                        str(connection_point_ref))

    """
    This method creates virtual link class object with all properties set and returns the same.
    """
    def handle_elan_links(self, virtual_link_elan, nsd_vl):
        virtual_link_inner = SonataSchema.VirtualLink(virtual_link_elan._id, virtual_link_elan.connectivity_type, [])
        for nf in nsd_vl.networkFunctions:
            for connection_point_ref in virtual_link_elan.connection_points_reference:
                if connection_point_ref in nf.connection_point_refs:
                    virtual_link_inner.connection_points_reference.append(str(connection_point_ref))
                else:
                    if connection_point_ref not in virtual_link_inner.connection_points_reference:
                        for connection_point in nsd_vl.connectionPoints:
                            if connection_point_ref == connection_point._id:
                                virtual_link_inner.connection_points_reference.append(str(connection_point_ref))
        return virtual_link_inner

    """
    This method returns 0 (false) or 1 (true) if the link passed as parameter has already been processed or not
    """
    def link_already_processed(self, nsd, vl):
        cp0 = vl.connection_points_reference[0]
        cp1 = vl.connection_points_reference[1]
        for nsd_vl in nsd.virtualLinks:
            if nsd_vl.connectivity_type == "E-Line":
                if cp0 in nsd_vl.connection_points_reference or cp1 in nsd_vl.connection_points_reference:
                    return 1
        return 0

    """
    This method returns a set of connection point refs of a all virtual function in a set
    """
    def get_connection_point_refs(self, virtual_function_set):
        connection_point_refs = []
        for virtual_function in virtual_function_set:
            for connection_point_ref in virtual_function.connection_point_refs:
                connection_point_refs.append(connection_point_ref)
        return connection_point_refs

    """
    This function splits the one to one virtual links between network functions. It also creates a new many to many
    virtual links.
    """
    def split_virtual_links(self):
        
        for i in range(len(self.NSDs)):
            nsd_vl = self.NSDs[i]
            for virtual_link in self.utilityFunctions.list_virtual_links:
                if virtual_link.connectivity_type == "E-LAN":
                    virtual_link_inner = self.handle_elan_links(virtual_link, nsd_vl)
                    nsd_vl.virtualLinks.append(virtual_link_inner)
                if virtual_link.connectivity_type == "E-Line":
                    virtual_link_inner = SonataSchema.VirtualLink(virtual_link._id, virtual_link.connectivity_type, [])
                    cp_0 = virtual_link.connection_points_reference[0]
                    cp_1 = virtual_link.connection_points_reference[1]
                    found_0 = 0
                    found_1 = 0
                    if cp_0 in self.get_connection_point_refs(nsd_vl.networkFunctions):
                        virtual_link_inner.connection_points_reference.append(str(cp_0))
                        found_0 = 1
                    else:
                        for connection_point in nsd_vl.connectionPoints:
                            if cp_0 == connection_point._id:
                                virtual_link_inner.connection_points_reference.append(str(cp_0))
                                found_0 = 1
                    if found_0 == 0:
                        if self.get_connection_point_type(cp_1) != "external":
                            virtual_link_inner.connection_points_reference.append(str("input"))
                            found_0 = 1
                    if cp_1 in self.get_connection_point_refs(nsd_vl.networkFunctions):
                        virtual_link_inner.connection_points_reference.append(str(cp_1))
                        found_1 = 1
                    else:
                        for connection_point in self.NSDs[i].connectionPoints:
                            if cp_1 == connection_point._id:
                                virtual_link_inner.connection_points_reference.append(str(cp_1))
                                found_1 = 1
                    if found_1 == 0:
                        if self.get_connection_point_type(cp_0) != "external":
                            virtual_link_inner.connection_points_reference.append(str("output"))
                            found_1 = 1
                    if len(virtual_link_inner.connection_points_reference) == 2:
                        str1 = virtual_link_inner.connection_points_reference[0].split(":")
                        str2 = virtual_link_inner.connection_points_reference[1].split(":")
                        if len(str1) == 2:
                            str1[0] = str1[0].replace("vnf_", "")
                        if len(str2) == 2:
                            str2[0] = str2[0].replace("vnf_", "")
                        virtual_link_inner._id = str1[0] + "-2-" + str2[0]
                        self.old_new_link_mapping.append([virtual_link._id, virtual_link_inner._id])
                    if found_0 == 1 and found_1 == 1:
                        _connection_point_type_0 = self.get_connection_point_type(
                            virtual_link_inner.connection_points_reference[0])
                        _connection_point_type_1 = self.get_connection_point_type(
                            virtual_link_inner.connection_points_reference[1])
                        if ( _connection_point_type_0 == "external" and _connection_point_type_1 == "external") == False:
                            nsd_vl.virtualLinks.append(virtual_link_inner)
            self.NSDs[i] = nsd_vl

    """
    This method takes original NSD and forwarding graph as an input. It returns constituent virtual link set containing 
    only those virtual links that are there in the forwarding graph.
    """
    def set_constituent_virtual_links(self, nsd, fg):
        constituent_vl = []
        for vl in nsd.virtualLinks:
            for virtual_links in fg.constituent_virtual_links:
                if vl._id == virtual_links:
                    constituent_vl.append(str(vl._id))
                    break
                else:
                    for old_new_mapping in self.old_new_link_mapping:
                        if vl._id == old_new_mapping[1] and virtual_links == old_new_mapping[0]:
                            constituent_vl.append(str(old_new_mapping[1]))
                            break
        return list(set(constituent_vl))

    """
    Method returns number of connection points of the virtual link provided in the argument
    """
    def number_of_connection_paths(self, constituent_vl):
        count = 0
        for vl in constituent_vl:
            if "input" in vl:
                count = count + 1
        return count

    """
    Returns true if the connection point reference is already processed, else returns false
    """
    def connection_point_already_processed(self, connection_point_ref):
        for connection_point_ref_path in self.processed_connection_point_path:
            if connection_point_ref_path[0] == connection_point_ref:
                if connection_point_ref_path[1] == 1:
                    return True
        return False

    """
    Method handles normal case where splitting results into parts maintaining sequence of virtual functions.  
    """
    def normal_case(self, path, nsd_fg):
        path_inner = SonataSchema.NetworkForwardingPaths(path.fp_id, path.policy, [])
        x = 1
        for cp in path.connection_points:
            if cp.connection_point_ref in self.get_connection_point_refs(nsd_fg.networkFunctions):
                point = SonataSchema.ConnectionPointsGraph(cp.connection_point_ref, x)
                path_inner.connection_points.append(point)
                x = x + 1
            else:
                for connection_point in nsd_fg.connectionPoints:
                    if cp.connection_point_ref == connection_point._id:
                        point = SonataSchema.ConnectionPointsGraph(cp.connection_point_ref, x)
                        path_inner.connection_points.append(point)
                        x = x + 1
        return path_inner

    """
    Method splits the forwarding path.
    """
    def split_forwarding_path(self):
        for i in range(len(self.NSDs)):
            nsd_fg = self.NSDs[i]
            del self.processed_connection_point_path[:]
            for fg in self.utilityFunctions.list_forwarding_graphs:
                
                fg_inner = SonataSchema.ForwardingGraphs(fg.fg_id, fg.number_of_endpoints,
                                               len(self.set_constituent_virtual_links(nsd_fg, fg)), self.network_function_sets[i],
                                               self.set_constituent_virtual_links(nsd_fg, fg), [])
                for path in fg.network_forwarding_path:
                    if self.number_of_connection_paths(self.set_constituent_virtual_links(nsd_fg, fg)) > 1:
                        for j in range(self.number_of_connection_paths(self.set_constituent_virtual_links(nsd_fg, fg))):
                            path_inner = SonataSchema.NetworkForwardingPaths(path.fp_id + "_" + str(j), path.policy, [])
                            x = 0
                            for cp in path.connection_points:
                                if self.connection_point_already_processed(cp.connection_point_ref) is False:
                                    found = 0
                                    if cp.connection_point_ref in self.get_connection_point_refs(nsd_fg.networkFunctions):
                                        x = x + 1
                                        point = SonataSchema.ConnectionPointsGraph(cp.connection_point_ref, x)
                                        path_inner.connection_points.append(point)
                                        found = 1
                                        self.processed_connection_point_path.append([cp.connection_point_ref, 1])
                                    else:
                                        for connection_point in nsd_fg.connectionPoints:
                                            if cp.connection_point_ref == connection_point._id:
                                                x = x + 1
                                                point = SonataSchema.ConnectionPointsGraph(cp.connection_point_ref, x)
                                                path_inner.connection_points.append(point)
                                                found = 1
                                                self.processed_connection_point_path.append([cp.connection_point_ref, 1])
                                    if found == 0:
                                        string = cp.connection_point_ref.split(":")
                                        if string[1] == "input":
                                            x = x + 1
                                            point = SonataSchema.ConnectionPointsGraph("output", x)
                                            path_inner.connection_points.append(point)
                                            self.processed_connection_point_path.append([cp.connection_point_ref, 1])
                                            break
                                        if string[1] == "output":
                                            x = 1
                                            point = SonataSchema.ConnectionPointsGraph("input", x)
                                            path_inner.connection_points.append(point)
                                            self.processed_connection_point_path.append([cp.connection_point_ref, 1])
                            fg_inner.network_forwarding_path.append(path_inner)
                    else:
                        fg_inner.network_forwarding_path.append(self.normal_case(path, nsd_fg))
                nsd_fg.forwardingGraphs.append(fg_inner)
            self.NSDs[i] = nsd_fg

    """
    Creates a file with all properties pulled from the objects created by above methods
    """
    def create_files(self):
        all_nsds=[]
        for i in range(len(self.NSDs)):
            data = {}
            data['descriptor_schema'] = str("https://raw.githubusercontent.com/sonata-nfv/tng-schema/master/service-descriptor/nsd-schema.yml")
            data['vendor'] = str(self.NSDs[i].vendor)
            data['name'] = str(self.NSDs[i].name)
            data['version'] = str(self.NSDs[i].version)
            data['author'] = str(self.NSDs[i].author)
            data['description'] = str(self.NSDs[i].description)

            data['network_functions'] = []
            for network_function in self.NSDs[i].networkFunctions:
                data['network_functions'].append({
                    "vnf_id": str(network_function.vnf_id),
                    "vnf_name": str(network_function.vnf_name),
                    "vnf_vendor": str(network_function.vnf_vendor),
                    "vnf_version": str(network_function.vnf_version)
                })

            data['connection_points'] = []
            for connection_point in self.NSDs[i].connectionPoints:
                data['connection_points'].append({
                    "id": str(connection_point._id),
                    "interface": str(connection_point.interface),
                    "type": str(connection_point._type)
                })

            data['virtual_links'] = []
            for virtual_link in self.NSDs[i].virtualLinks:
                data['virtual_links'].append({
                    "id": str(virtual_link._id),
                    "connectivity_type": str(virtual_link.connectivity_type),
                    "connection_points_reference": virtual_link.connection_points_reference
                })

            sub_data = {}
            sub_data['network_forwarding_paths'] = []
            for network_forwarding_path in self.NSDs[i].forwardingGraphs[0].network_forwarding_path:

                sub_data['connection_points'] = []

                for connection_point in network_forwarding_path.connection_points:
                    sub_data['connection_points'].append({
                        "connection_point_ref": str(connection_point.connection_point_ref),
                        "position": connection_point.position
                    })
                sub_data['network_forwarding_paths'].append({
                    "fp_id": str(network_forwarding_path.fp_id),
                    "policy": str(network_forwarding_path.policy),
                    "connection_points": sub_data['connection_points']
                })

            data['forwarding_graphs'] = []
            for forwarding_graph in self.NSDs[i].forwardingGraphs:
                if len(forwarding_graph.constituent_virtual_links) != 0:
                    print(len(forwarding_graph.constituent_virtual_links))
                    data['forwarding_graphs'].append({
                        "fg_id": str(forwarding_graph.fg_id),
                        "number_of_endpoints": forwarding_graph.number_of_endpoints,
                        "number_of_virtual_links": forwarding_graph.number_of_virtual_links,
                        "constituent_virtual_links": forwarding_graph.constituent_virtual_links,
                        "constituent_vnfs": forwarding_graph.constituent_vnfs,
                        "network_forwarding_paths": sub_data['network_forwarding_paths']
                    })
                else:
                    data['forwarding_graphs'].append({
                        "fg_id": str(forwarding_graph.fg_id),
                        "number_of_endpoints": forwarding_graph.number_of_endpoints,
                        "number_of_virtual_links": forwarding_graph.number_of_virtual_links,
                        "constituent_vnfs": forwarding_graph.constituent_vnfs,
                        "network_forwarding_paths": sub_data['network_forwarding_paths']
                    })

            all_nsds.append(data)
        
        #file_name = "NSD_" + str(i)
            #with open(file_name + '.yml', 'w') as outfile:
                #print("Creating NSD_" + str(i))
                #yaml.dump(data, outfile, default_flow_style=False)
                #print("Created NSD_" + str(i))
        return all_nsds

    def split_sonata(self):
        if self.validate() is not False:
            self.create_new_function_sets()
            self.set_connection_point_refs_for_virtual_functions()
            self.split_network_function()
            self.set_connection_points()
            self.split_virtual_links()
            self.split_forwarding_path()
            self.set_general_information()
            return self.create_files()
        else:
            print("Validation Failed!!")
