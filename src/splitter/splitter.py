from nameko.rpc import rpc
import SonataSchema as SS
import SonataUtilityFunctions as utilityFunctions
import json
import pymongo


NSDs = []
#network_function_sets = [["vnf_iperf"], ["vnf_tcpdump"], ["vnf_firewall"]]
network_function_sets = [["vnf_iperf", "vnf_tcpdump"], ["vnf_firewall"]]
#network_function_sets = [["vnf_iperf", "vnf_firewall"], ["vnf_tcpdump"]]
old_new_link_mapping = []


class SplitterService:
    name = "splitter_service"

    @rpc
    def hello(self, name):
        return "Success"


def get_network_function_object(vnf_name):
    for nf_object in utilityFunctions.list_nf:
        if nf_object.vnf_id == vnf_name:
            return nf_object
    return None


def split_network_function():
    for network_function_set in network_function_sets:
        sub_nsd = SS.NSD("", "", "", "", "", "", [], [], [], [])
        network_function_list = []
        for network_function in network_function_set:
            network_function_list.append(get_network_function_object(network_function))
            sub_nsd.networkFunctions = network_function_list
        NSDs.append(sub_nsd)


def set_connection_points():
    for i in range(len(network_function_sets)):
        nsd_cp = NSDs[i]
        nsd_cp.connectionPoints = utilityFunctions.list_connection_points
        NSDs[i] = nsd_cp


def set_general_information():
    for i in range(len(network_function_sets)):
        nsd_general_info = NSDs[i]
        nsd_general_info.descriptor_version = utilityFunctions.descriptor_version
        nsd_general_info.vendor = utilityFunctions.vendor
        nsd_general_info.name = utilityFunctions.name
        nsd_general_info.version = utilityFunctions.version
        nsd_general_info.author = utilityFunctions.author
        nsd_general_info.description = utilityFunctions.description
        NSDs[i] = nsd_general_info


def set_connection_point_refs_for_virtual_functions():
    for virtual_link in utilityFunctions.list_virtual_links:
        for connection_point_ref in virtual_link.connection_points_reference:
            split_string = connection_point_ref.split(':')
            if get_network_function_object(split_string[0]) is not None:
                get_network_function_object(split_string[0]).connection_point_refs.append(str(connection_point_ref))


def handle_elan_links(virtual_link_elan, nsd_vl):
    virtual_link_inner = SS.VirtualLink(virtual_link_elan.id, virtual_link_elan.connectivity_type, [])
    for nf in nsd_vl.networkFunctions:
        for connection_point_ref in virtual_link_elan.connection_points_reference:
            if connection_point_ref in nf.connection_point_refs:
                virtual_link_inner.connection_points_reference.append(str(connection_point_ref))
            else:
                if connection_point_ref not in virtual_link_inner.connection_points_reference:
                    for connection_point in nsd_vl.connectionPoints:
                        if connection_point_ref == connection_point.id:
                            virtual_link_inner.connection_points_reference.append(str(connection_point_ref))
    return virtual_link_inner


def link_already_processed(nsd, vl):
    cp0 = vl.connection_points_reference[0]
    cp1 = vl.connection_points_reference[1]
    for nsd_vl in nsd.virtualLinks:
        if nsd_vl.connectivity_type == "E-Line":
            if cp0 in nsd_vl.connection_points_reference or cp1 in nsd_vl.connection_points_reference:
                return 1
    return 0


def get_connection_point_refs(virtual_function_set):
    connection_point_refs = []
    for virtual_function in virtual_function_set:
        for connection_point_ref in virtual_function.connection_point_refs:
            connection_point_refs.append(connection_point_ref)
    return connection_point_refs


def split_virtual_links():
    for i in range(len(NSDs)):
        nsd_vl = NSDs[i]
        for virtual_link in utilityFunctions.list_virtual_links:
            if virtual_link.connectivity_type == "E-LAN":
                virtual_link_inner = handle_elan_links(virtual_link, nsd_vl)
                nsd_vl.virtualLinks.append(virtual_link_inner)
            if virtual_link.connectivity_type == "E-Line":
                if link_already_processed(nsd_vl, virtual_link) == 0:
                    virtual_link_inner = SS.VirtualLink(virtual_link.id, virtual_link.connectivity_type, [])
                    cp_0 = virtual_link.connection_points_reference[0]
                    cp_1 = virtual_link.connection_points_reference[1]
                    if len(virtual_link_inner.connection_points_reference) < 2:
                        found_0 = 0
                        found_1 = 0
                        if cp_0 in get_connection_point_refs(nsd_vl.networkFunctions):
                            virtual_link_inner.connection_points_reference.append(str(cp_0))
                            found_0 = 1
                        else:
                            for connection_point in nsd_vl.connectionPoints:
                                if cp_0 == connection_point.id:
                                    virtual_link_inner.connection_points_reference.append(str(cp_0))
                                    found_0 = 1
                        if found_0 == 0:
                            print(cp_0)
                        if cp_1 in get_connection_point_refs(nsd_vl.networkFunctions):
                            virtual_link_inner.connection_points_reference.append(str(cp_1))
                            found_1 = 1
                        else:
                            for connection_point in NSDs[i].connectionPoints:
                                if cp_1 == connection_point.id:
                                    virtual_link_inner.connection_points_reference.append(str(cp_1))
                                    found_1 = 1
                        if found_1 == 0:
                            split_string = cp_1.split(':')
                            vnf_containing_vl = []
                            for virtual_link_temp in utilityFunctions.list_virtual_links:
                                if virtual_link_temp.connectivity_type == "E-Line":
                                    if split_string[0] in virtual_link_temp.connection_points_reference[0]\
                                            or split_string[0] in virtual_link_temp.connection_points_reference[1]:
                                        vnf_containing_vl.append(virtual_link_temp)
                            for vnf_containing_vl_temp in vnf_containing_vl:
                                if vnf_containing_vl_temp.id != virtual_link.id:
                                    if split_string[0] not in vnf_containing_vl_temp.connection_points_reference[0]:
                                        virtual_link_inner.connection_points_reference.append(
                                            str(vnf_containing_vl_temp.connection_points_reference[0]))
                                    if split_string[0] not in vnf_containing_vl_temp.connection_points_reference[1]:
                                        virtual_link_inner.connection_points_reference.append(
                                            str(vnf_containing_vl_temp.connection_points_reference[1]))
                    if len(virtual_link_inner.connection_points_reference) == 2:
                        str1 = virtual_link_inner.connection_points_reference[0].split(":")
                        str2 = virtual_link_inner.connection_points_reference[1].split(":")
                        if len(str1) == 2:
                            str1[0] = str1[0].replace("vnf_", "")
                        if len(str2) == 2:
                            str2[0] = str2[0].replace("vnf_", "")
                        virtual_link_inner.id = str1[0] + "-2-" + str2[0]
                        old_new_link_mapping.append([virtual_link.id, virtual_link_inner.id])
                    nsd_vl.virtualLinks.append(virtual_link_inner)
        NSDs[i] = nsd_vl


def set_constituent_virtual_links(nsd, fg):
    constituent_vl = []
    for vl in nsd.virtualLinks:
        for virtual_links in fg.constituent_virtual_links:
            if vl.id == virtual_links:
                constituent_vl.append(str(vl.id))
                break
            else:
                for old_new_mapping in old_new_link_mapping:
                    if vl.id == old_new_mapping[0]:
                        constituent_vl.append(str(old_new_mapping[1]))
                        break
    return list(set(constituent_vl))


def split_forwarding_path():
    for i in range(len(NSDs)):
        nsd_fg = NSDs[i]
        for fg in utilityFunctions.list_forwarding_graphs:
            fg_inner = SS.ForwardingGraphs(fg.fg_id, fg.number_of_endpoints,
                                           len(set_constituent_virtual_links(nsd_fg, fg)), network_function_sets[i],
                                           set_constituent_virtual_links(nsd_fg, fg), [])
            for path in fg.network_forwarding_path:
                path_inner = SS.NetworkForwardingPaths(path.fp_id, path.policy, [])
                x = 1
                for cp in path.connection_points:
                    if cp.connection_point_ref in get_connection_point_refs(nsd_fg.networkFunctions):
                        point = SS.ConnectionPointsGraph(cp.connection_point_ref, x)
                        path_inner.connection_points.append(point)
                        x = x + 1
                    else:
                        for connection_point in nsd_fg.connectionPoints:
                            if cp.connection_point_ref == connection_point.id:
                                point = SS.ConnectionPointsGraph(cp.connection_point_ref, x)
                                path_inner.connection_points.append(point)
                                x = x + 1
                fg_inner.network_forwarding_path.append(path_inner)
            nsd_fg.forwardingGraphs.append(fg_inner)
        NSDs[i] = nsd_fg


def create_files():
    for i in range(len(NSDs)):
        data = {}
        data['descriptor_version'] = str(NSDs[i].descriptor_version)
        data['vendor'] = str(NSDs[i].vendor)
        data['name'] = str(NSDs[i].name)
        data['version'] = str(NSDs[i].version)
        data['author'] = str(NSDs[i].author)
        data['description'] = str(NSDs[i].description)

        data['network_functions'] = []
        for network_function in NSDs[i].networkFunctions:
            data['network_functions'].append({
                "vnf_id": str(network_function.vnf_id),
                "vnf_name": str(network_function.vnf_name),
                "vnf_vendor": str(network_function.vnf_vendor),
                "vnf_version": str(network_function.vnf_version)
            })

        data['connection_points'] = []
        for connection_point in NSDs[i].connectionPoints:
            data['connection_points'].append({
                "id": str(connection_point.id),
                "interface": str(connection_point.interface),
                "type": str(connection_point.type)
            })

        data['virtual_links'] = []
        for virtual_link in NSDs[i].virtualLinks:
            data['virtual_links'].append({
                "id": str(virtual_link.id),
                "connectivity_type": str(virtual_link.connectivity_type),
                "connection_points_reference": virtual_link.connection_points_reference
            })

        sub_data = {}
        sub_data['connection_points'] = []

        for connection_point in NSDs[i].forwardingGraphs[0].network_forwarding_path[0].connection_points:
            sub_data['connection_points'].append({
                "connection_point_ref": str(connection_point.connection_point_ref),
                "position": str(connection_point.position)
            })

        sub_data['network_forwarding_paths'] = []
        for network_forwarding_path in NSDs[i].forwardingGraphs[0].network_forwarding_path:
            sub_data['network_forwarding_paths'].append({
                "fp_id": str(network_forwarding_path.fp_id),
                "policy": str(network_forwarding_path.policy),
                "connection_points": sub_data['connection_points']
            })

        data['forwarding_graphs'] = []
        for forwarding_graph in NSDs[i].forwardingGraphs:
            data['forwarding_graphs'].append({
                "fg_id": str(forwarding_graph.fg_id),
                "number_of_endpoints": str(forwarding_graph.number_of_endpoints),
                "number_of_virtual_links": str(forwarding_graph.number_of_virtual_links),
                "constituent_virtual_links": forwarding_graph.constituent_virtual_links,
                "constituent_vnfs": forwarding_graph.constituent_vnfs,
                "network_forwarding_paths": sub_data['network_forwarding_paths']
            })

        file_name = "Sonata_" + str(i)
        with open(file_name + '.json', 'w') as outfile:
            print("Creating NSD_" + str(i))
            json.dump(data, outfile) #default_flow_style=False)
            print("Created NSD_" + str(i))

        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["scramble_nsd"]
        check = db["sonata_nsd"]
        with open('Sonata_' +str(i) +'.json') as f:
            file_data = json.load(f)
        check.insert_one(file_data)
def split_sonata():
    set_connection_point_refs_for_virtual_functions()
    split_network_function()
    set_connection_points()
    split_virtual_links()
    split_forwarding_path()
    set_general_information()
    create_files()
