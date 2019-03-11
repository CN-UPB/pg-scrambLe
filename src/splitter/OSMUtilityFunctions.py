import OsmSchema as osm_schema


id = ""
name = ""
short_name = ""
description = ""
vendor = ""
version = ""
logo = ""

list_vnfd_connection_point_ref = []
list_vld = []
list_constituent_vnfd = []
list_nsd = []
list_dns_server = []
list_dhcp_params = []
list_connection_point = []
list_scaling_criteria = []
list_scaling_policy = []
list_vnfd_member = []
list_scaling_config_action = []
list_scaling_group_descriptor = []
list_vnfd_connection_point_ref = []
list_rsp = []
list_match_attributes = []
list_classifier = []
list_vnffgd = []
list_vnf_dependency = []
list_ip_profiles = []


def get_osm_nsd(received_file_sonata):
    source = received_file_sonata[0]
    for key in source.keys():
        if key == "nsd:nsd-catalog":
            nsd = source[key]
            for nsd_key in nsd.keys():
                nsd_temp = nsd[nsd_key]
                set_vnffg(nsd_temp[0])
                call_functions(nsd_temp[0])


def set_general_informations(source):
    global id
    id = source['id']
    global name
    name = source['name']
    global short_name
    short_name = source['short-name']
    global description
    description = source['description']
    global vendor
    vendor = source['vendor']
    global version
    version = source['version']
    global logo
    logo = source['logo']


def set_constituent_vnfd(source):
    constituent_vnfd = source['constituent-vnfd']
    for constituent_vnfd_data in constituent_vnfd:
        member_vnf_index = constituent_vnfd_data.get('member-vnf-index')
        vnfd_id_ref = constituent_vnfd_data.get('vnfd-id-ref')
        start_by_default = constituent_vnfd_data.get('start-by-default')
        constituent_vnfd_instance = osm_schema.ConstituentVnfd(member_vnf_index, start_by_default, vnfd_id_ref)
        list_constituent_vnfd.append(constituent_vnfd_instance)


def set_ip_profiles(source):
    ip_profiles = source['ip-profiles']
    for ip_profiles_data in ip_profiles:
        name = ip_profiles_data['name']
        description = ip_profiles_data.get('description')
        ip_profile_params = ip_profiles_data['ip-profile-params']
        gateway_address = ip_profile_params.get('gateway-address')
        ip_version = ip_profile_params.get('ip-version')
        subnet_address = ip_profile_params.get('subnet-address')
        subnet_prefix_pool = ip_profile_params.get('subnet-prefix-pool')
        security_group = ip_profile_params.get('security_group')

        dns_server_data = ip_profile_params.get('dns-server')
        for dns_server_address in dns_server_data:
            address = dns_server_address.get('address')
            dns_server_instance = osm_schema.DnsServer(address)
            list_dns_server.append(dns_server_instance)

        dhcp_params = ip_profile_params.get('dhcp-params')
        enabled = dhcp_params.get('enabled')
        start_address = dhcp_params.get('start-address')
        count = dhcp_params.get('count')
        dhcp_params_instance = osm_schema.DhcpParams(enabled, start_address, count)
        list_dhcp_params.append(dhcp_params_instance)

        ip_profile_params_instance = osm_schema.IpProfileParams(ip_version, subnet_address, gateway_address,
                                                                security_group, list_dns_server,
                                                                list_dhcp_params, subnet_prefix_pool)
        ip_profiles_instance = osm_schema.IpProfiles(name, description, ip_profile_params_instance)
        list_ip_profiles.append(ip_profiles_instance)


def set_vld(source):
    vld = source['vld']
    for vld_data in vld:
        id = vld_data.get('id')
        name = vld_data.get('name')
        short_name = vld_data.get('short-name')
        vendor = vld_data.get('vendor')
        description = vld_data.get('description')
        version = vld_data.get('version')
        type = vld_data.get('type')
        root_bandwidth = vld_data.get('root_bandwidth')
        leaf_bandwidth = vld_data.get('leaf_bandwidth')
        mgmt_network = vld_data.get('mgmt-network')
        vim_network_name = vld_data.get('vim-network-name')
        ip_profile_ref = vld_data.get('ip-profile-ref')
        vnfd_connection_point_ref = vld_data.get('vnfd-connection-point-ref')
        for vnfd_connection_point_ref_data in vnfd_connection_point_ref:
            member_vnf_index_ref = vnfd_connection_point_ref_data.get('member-vnf-index-ref')
            order = vnfd_connection_point_ref_data.get('order')
            vnfd_id_ref = vnfd_connection_point_ref_data.get('vnfd-id-ref')
            vnfd_connection_point_ref = vnfd_connection_point_ref_data.get('vnfd-connection-point-ref')
            # print(vnfd_connection_point_ref)
            vnfd_connection_point_ref_instance = osm_schema.VnfdConnectionPointRef(member_vnf_index_ref, order,
                                                                                   vnfd_id_ref,
                                                                                   vnfd_connection_point_ref)
            list_vnfd_connection_point_ref.append(vnfd_connection_point_ref_instance)

        vld_instance = osm_schema.Vld(id, name, short_name, vendor, description, version, type, root_bandwidth,
                                      leaf_bandwidth, mgmt_network, vim_network_name, ip_profile_ref,
                                      list_vnfd_connection_point_ref)
        list_vld.append(vld_instance)


def set_vnffg(source):
    vnffgd = source['vnffgd']
    for vnffgd_data in vnffgd:
        id = vnffgd_data.get('id')
        name = vnffgd_data.get('name')
        short_name = vnffgd_data.get('short_name')
        vendor = vnffgd_data.get('vendor')
        description = vnffgd_data.get('description')
        version = vnffgd_data.get('id')
        rsp = vnffgd_data['rsp']
        for rsp_data in rsp:
            id = rsp_data.get('id')
            name = rsp_data.get('name')
            member_vnf_index_ref = rsp_data.get('member_vnf_index_ref')
            order = rsp_data.get('order')
            vnfd_id_ref = rsp_data.get('vnfd_id_ref')
            vnfd_connection_point_ref = rsp_data.get('vnfd-connection-point-ref')
            rsp_instance = osm_schema.Rsp(id, name, vnfd_connection_point_ref, member_vnf_index_ref, order, vnfd_id_ref)
            list_rsp.append(rsp_instance)
            classifier = vnffgd_data['classifier']
            for classifier_data in classifier:
                id = classifier_data.get('id')
                name = classifier_data.get('name')
                rsp_id_ref = classifier_data.get('rsp_id_ref')
                member_vnf_index_ref = classifier_data.get('member_vnf_index_ref')
                vnfd_id_ref = classifier_data.get('vnfd_id_ref')
                vnfd_connection_point_ref = classifier_data.get('vnfd_connection_point_ref')
                match_attributes = classifier_data['match-attributes']
                for match_attributes_data in match_attributes:
                    id = match_attributes_data.get('id')
                    ip_proto = match_attributes_data.get('ip_proto')
                    source_ip_address = match_attributes_data.get('source_ip_address')
                    destination_ip_address = match_attributes_data.get('destination_ip_address')
                    source_port = match_attributes_data.get('source_port')
                    destination_port = match_attributes_data.get('destination_port')
                    match_attributes_instance = osm_schema.MatchAttributes(id, ip_proto, source_ip_address,
                                                                                       destination_ip_address,
                                                                                       source_port, destination_port)
                    list_match_attributes.append(match_attributes_instance)

                classifier_instance = osm_schema.Classifier(id, name, rsp_id_ref, list_match_attributes,
                                                                member_vnf_index_ref, vnfd_id_ref,
                                                                vnfd_connection_point_ref)
                list_classifier.append(classifier_instance)
        vnffgd_instance = osm_schema.Vnffgd(id, name, short_name, vendor, description, version, list_rsp,
                                            list_classifier)
        list_vnffgd.append(vnffgd_instance)


def call_functions(source):
    set_general_informations(source)
    set_constituent_vnfd(source)
    set_ip_profiles(source)
    set_vld(source)
    set_vnffg(source)
