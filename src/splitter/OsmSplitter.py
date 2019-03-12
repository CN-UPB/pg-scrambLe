import OsmSchema as OS
import OSMUtilityFunctions as utilityFunctions
import yaml

NSDs = []
network_function_sets = [["1", "2"], ["3"]]


def get_network_function_object(vnf_index):
    for nf_object in utilityFunctions.list_constituent_vnfd:
        if str(nf_object.member_vnf_index) == vnf_index:
            return nf_object
    return None


def handle_elan_links(virtual_link_elan, nsd_vl):
    vld_instance = OS.Vld(virtual_link_elan.id, virtual_link_elan.name, virtual_link_elan.short_name,
                          virtual_link_elan.vendor, virtual_link_elan.description, virtual_link_elan.version,
                          virtual_link_elan.type, virtual_link_elan.root_bandwidth, virtual_link_elan.leaf_bandwidth,
                          virtual_link_elan.mgmt_network, virtual_link_elan.vim_network_name,
                          virtual_link_elan.ip_profile_ref, [])
    for vnf in nsd_vl.ConstituentVnfd:
        for vnfd_connection_point_ref_inner in virtual_link_elan.vnfd_connection_point_ref_vld:
            if vnfd_connection_point_ref_inner is not None and vnf is not None:
                if vnfd_connection_point_ref_inner.member_vnf_index_ref == vnf.member_vnf_index:
                    vld_instance.vnfd_connection_point_ref_vld.append(vnfd_connection_point_ref_inner)
    return vld_instance


def split_network_function():
    for network_function_set in network_function_sets:
        sub_nsd = OS.Nsd("", "", "", "", "", "", "", [], [], [], [], [])
        network_function_list = []
        for network_function in network_function_set:
            network_function_list.append(get_network_function_object(network_function))
        sub_nsd.ConstituentVnfd = network_function_list
        NSDs.append(sub_nsd)


def set_ip_profiles():
    for i in range(len(network_function_sets)):
        nsd_ip_profiles = NSDs[i]
        nsd_ip_profiles.ip_profiles = utilityFunctions.list_ip_profiles
        NSDs[i] = nsd_ip_profiles


def set_general_information():
    for i in range(len(network_function_sets)):
        nsd_general_info = NSDs[i]
        nsd_general_info.id = utilityFunctions.id
        nsd_general_info.name = utilityFunctions.name
        nsd_general_info.short_name = utilityFunctions.short_name
        nsd_general_info.description = utilityFunctions.description
        nsd_general_info.vendor = utilityFunctions.vendor
        nsd_general_info.version = utilityFunctions.version
        nsd_general_info.logo = utilityFunctions.logo
        NSDs[i] = nsd_general_info


def split_vld():
    for i in range(len(NSDs)):
        nsd_vld = NSDs[i]
        for virtual_link in utilityFunctions.list_vld:
            if virtual_link.type == "ELAN":
                virtual_link_inner = handle_elan_links(virtual_link, nsd_vld)
                nsd_vld.vld.append(virtual_link_inner)
        NSDs[i] = nsd_vld


def split_forwarding_path():
    for i in range(len(NSDs)):
        nsd_fg = NSDs[i]
        for fg in utilityFunctions.list_vnffgd:
            vnffgd_instance = OS.Vnffgd(fg.id, fg.name, fg.short_name, fg.vendor, fg.description, fg.version, [], [])
            for classifier in fg.classifier:
                for constituent_vnf in nsd_fg.ConstituentVnfd:
                    if classifier is not None and constituent_vnf is not None:
                        if str(classifier.member_vnf_index_ref) == str(constituent_vnf.member_vnf_index):
                            vnffgd_instance.classifier.append(classifier)
            for rsp in fg.rsp:
                if rsp.id is not None:
                    vnffgd_instance.rsp.append(rsp)
                for constituent_vnf in nsd_fg.ConstituentVnfd:
                    if rsp.id is None:
                        if str(rsp.member_vnf_index_ref) == str(constituent_vnf.member_vnf_index):
                            vnffgd_instance.rsp.append(rsp)
        nsd_fg.vnffgd.append(vnffgd_instance)
        NSDs[i] = nsd_fg


def create_files():
    for i in range(len(NSDs)):
        data = {}

        constituent_vnfds = {}
        constituent_vnfds['constituent-vnfd'] = []
        for constituent_vnfd in NSDs[i].ConstituentVnfd:
            constituent_vnfds['constituent-vnfd'].append({
                "member-vnf-index": str(constituent_vnfd.member_vnf_index),
                "vnfd-id-ref": str(constituent_vnfd.vnfd_id_ref)
            })

        dns_server = {}
        dns_server['dns-server'] = []
        for ip_profile_data in NSDs[i].ip_profiles:
            dns_server['dns-server'].append({
                "address": str(ip_profile_data.ip_profile_params.dns_server[0].address),
                "address": str(ip_profile_data.ip_profile_params.dns_server[1].address)
            })

        dhcp_params = {}
        dhcp_params['dhcp-params'] = []
        for ip_profile_data in NSDs[i].ip_profiles:
            dhcp_params['dhcp-params'].append({
                "count": str(ip_profile_data.ip_profile_params.dhcp_params[0].count),
                "start-address": str(ip_profile_data.ip_profile_params.dhcp_params[0].start_address)
            })

        ip_profile_params = {}
        ip_profile_params['ip-profile-params'] = []
        for ip_profile_data in NSDs[i].ip_profiles:
            ip_profile_params['ip-profile-params'].append({
                "gateway-address": str(ip_profile_data.ip_profile_params.gateway_address),
                "ip-version": str(ip_profile_data.ip_profile_params.ip_version),
                "subnet-address": str(ip_profile_data.ip_profile_params.subnet_address),
                "dns-server": dns_server['dns-server'],
                "dhcp-params": dhcp_params['dhcp-params']
            })


        ip_profile = {}
        ip_profile['ip-profiles'] = []
        for ip_profile_data in NSDs[i].ip_profiles:
            ip_profile['ip-profiles'].append({
                "name": str(ip_profile_data.name),
                "description": str(ip_profile_data.description),
                "ip-profile-params": ip_profile_params['ip-profile-params']
            })

        vnfd_connection_point_ref = {}
        vnfd_connection_point_ref['vnfd-connection-point-ref'] = []
        for vnfd_connection_point_ref_data in NSDs[i].vld[0].vnfd_connection_point_ref_vld:
            vnfd_connection_point_ref['vnfd-connection-point-ref'].append({
                "member-vnf-index-ref": str(vnfd_connection_point_ref_data.member_vnf_index_ref),
                "vnfd-id-ref": str(vnfd_connection_point_ref_data.vnfd_id_ref),
                "vnfd-connection-point-ref": str(vnfd_connection_point_ref_data.vnfd_connection_point_ref)
            })

        vld = {}
        vld['vld'] = []
        for vld_data in NSDs[i].vld:
            vld['vld'].append({
                "id": str(vld_data.id),
                "name": str(vld_data.name),
                "short-name": str(vld_data.short_name),
                "type": str(vld_data.type),
                "ip-profile-ref": str(vld_data.ip_profile_ref),
                "vnfd-connection-point-ref": vnfd_connection_point_ref['vnfd-connection-point-ref']
            })

        match_attributes = {}
        match_attributes['match-attributes'] = []
        for vnffgd_data in NSDs[i].vnffgd:
            for classifier_data in vnffgd_data.classifier:
                for match_attribute in classifier_data.match_attributes:
                    match_attributes['match-attributes'].append({
                        "id": str(match_attribute.id),
                        "ip-proto": str(match_attribute.ip_proto),
                        "source-ip-address": str(match_attribute.source_ip_address),
                        "destination-ip-address": str(match_attribute.destination_ip_address),
                        "source-port": str(match_attribute.source_port),
                        "destination-port": str(match_attribute.destination_port)
                    })

        classifier = {}
        classifier['classifier'] = []
        for vnffgd_data in NSDs[i].vnffgd:
            for classifier_data in vnffgd_data.classifier:
                classifier['classifier'].append({
                    "id": str(classifier_data.id),
                    "name": str(classifier_data.name),
                    "rsp-id-ref": str(classifier_data.rsp_id_ref),
                    "member-vnf-index-ref": str(classifier_data.member_vnf_index_ref),
                    "vnfd-id-ref": str(classifier_data.vnfd_id_ref),
                    "vnfd-connection-point-ref": str(classifier_data.vnfd_connection_point_ref),
                    "match-attributes": match_attributes['match-attributes']
                })

        rsp = {}
        rsp['rsp'] = []
        for vnffgd_data in NSDs[i].vnffgd:
            for rsp_data in vnffgd_data.rsp:
                if rsp_data.id is not None:
                    rsp['rsp'].append({
                        "id": str(rsp_data.id),
                        "name": str(rsp_data.name),
                        "vnfd-connection-point-ref": ""
                    })
                else:
                    rsp['rsp'].append({
                        "member-vnf-index-ref": str(rsp_data.member_vnf_index_ref),
                        "order": str(rsp_data.order),
                        "vnfd-id-ref": str(rsp_data.vnf_id_ref),
                        "vnfd-connection-point-ref": str(rsp_data.vnfd_connection_point_ref)
                    })

        vnffgd = {}
        vnffgd['vnffgd'] = []
        if bool(classifier):
            for vnffgd_data in NSDs[i].vnffgd:
                vnffgd['vnffgd'].append({
                    "id": str(vnffgd_data.id),
                    "name": str(vnffgd_data.name),
                    "short-name": str(vnffgd_data.short_name),
                    "description": str(vnffgd_data.description),
                    "vendor": str(vnffgd_data.vendor),
                    "version": str(vnffgd_data.version),
                    "rsp": rsp['rsp'],
                })
        else:
            for vnffgd_data in NSDs[i].vnffgd:
                vnffgd['vnffgd'].append({
                    "id": str(vnffgd_data.id),
                    "name": str(vnffgd_data.name),
                    "short-name": str(vnffgd_data.short_name),
                    "description": str(vnffgd_data.description),
                    "vendor": str(vnffgd_data.vendor),
                    "version": str(vnffgd_data.version),
                    "rsp": rsp['rsp'],
                    "classifier": classifier['classifier']
                })

        general_information = {}
        general_information['nsd'] = []
        general_information['nsd'].append({
            "id": str(NSDs[i].id),
            "name": str(NSDs[i].name),
            "short-name": str(NSDs[i].short_name),
            "description": str(NSDs[i].description),
            "vendor": str(NSDs[i].vendor),
            "version": str(NSDs[i].version),
            "logo": str(NSDs[i].logo),
            "constituent-vnfd": constituent_vnfds['constituent-vnfd'],
            "ip-profiles": ip_profile['ip-profiles'],
            "vld": vld['vld'],
            "vnffgd": vnffgd['vnffgd']
        })

        data['nsd:nsd-catalog'] = {
            "nsd": general_information['nsd']
        }


        file_name = "OSM_NSD_" + str(i)
        with open(file_name + '.yml', 'w') as outfile:
            print("Creating OSM NSD_" + str(i))
            yaml.dump(data, outfile, default_flow_style=False)
            print("Created OSM NSD_" + str(i))


def split_osm():
    split_network_function()
    set_ip_profiles()
    split_vld()
    split_forwarding_path()
    set_general_information()
    create_files()
