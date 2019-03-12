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
                call_functions(nsd_temp[0])


def set_general_informations(source):
    global id
    id = source.get('id')
    global name
    name = source.get('name')
    global short_name
    short_name = source.get('short-name')
    global description
    description = source.get('description')
    global vendor
    vendor = source.get('vendor')
    global version
    version = source.get('version')
    global logo
    logo = source.get('logo')


def set_constituent_vnfd(source):
    constituent_vnfd = source['constituent-vnfd']
    for constituent_vnfd_data in constituent_vnfd:
        member_vnf_index = constituent_vnfd_data.get('member-vnf-index')
        vnfd_id_ref = constituent_vnfd_data.get('vnfd-id-ref')
        start_by_default = constituent_vnfd_data.get('start-by-default')
        constituent_vnfd_instance = osm_schema.ConstituentVnfd(member_vnf_index, start_by_default, vnfd_id_ref)
        list_constituent_vnfd.append(constituent_vnfd_instance)


def set_ip_profiles(source):
    ip_profiles = source.get('ip-profiles')
    if ip_profiles is not None:
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
        vnfd_connection_point_ref_vld = vld_data.get('vnfd-connection-point-ref')
        for vnfd_connection_point_ref_data in vnfd_connection_point_ref_vld:
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
    vnffgd = source.get('vnffgd')
    if vnffgd is not None:
        for vnffgd_data in vnffgd:
            vnffgd_id = vnffgd_data.get('id')
            vnffgd_name = vnffgd_data.get('name')
            vnffgd_short_name = vnffgd_data.get('short-name')
            vnffgd_vendor = vnffgd_data.get('vendor')
            vnffgd_description = vnffgd_data.get('description')
            vnffgd_version = vnffgd_data.get('version')
            rsp = vnffgd_data['rsp']
            for rsp_data in rsp:
                rsp_id = rsp_data.get('id')
                rsp_name = rsp_data.get('name')
                rsp_vnfd_connection_point_ref = rsp_data.get('vnfd-connection-point-ref')
                rsp_member_vnf_index_ref = rsp_data.get('member-vnf-index-ref')
                rsp_order = rsp_data.get('order')
                rsp_vnfd_id_ref = rsp_data.get('vnfd-id-ref')
                rsp_instance = osm_schema.Rsp(rsp_id, rsp_name, rsp_vnfd_connection_point_ref, rsp_member_vnf_index_ref, rsp_order, rsp_vnfd_id_ref)
                list_rsp.append(rsp_instance)
            classifier = vnffgd_data['classifier']
            for classifier_data in classifier:
                classifier_id = classifier_data.get('id')
                classifier_name = classifier_data.get('name')
                classifier_rsp_id_ref = classifier_data.get('rsp-id-ref')
                classifier_member_vnf_index_ref = classifier_data.get('member-vnf-index-ref')
                classifier_vnfd_id_ref = classifier_data.get('vnfd-id-ref')
                classifier_vnfd_connection_point_ref = classifier_data.get('vnfd-connection-point-ref')
                match_attributes = classifier_data['match-attributes']
                for match_attributes_data in match_attributes:
                    match_attributes_id = match_attributes_data.get('id')
                    match_attributes_ip_proto = match_attributes_data.get('ip-proto')
                    match_attributes_source_ip_address = match_attributes_data.get('source-ip-address')
                    match_attributes_destination_ip_address = match_attributes_data.get('destination-ip-address')
                    match_attributes_source_port = match_attributes_data.get('source-port')
                    match_attributes_destination_port = match_attributes_data.get('destination-port')
                    match_attributes_instance = osm_schema.MatchAttributes(match_attributes_id, match_attributes_ip_proto, match_attributes_source_ip_address,
                                                                                       match_attributes_destination_ip_address,
                                                                                       match_attributes_source_port, match_attributes_destination_port)
                    list_match_attributes.append(match_attributes_instance)

                classifier_instance = osm_schema.Classifier(classifier_id, classifier_name, classifier_rsp_id_ref, list_match_attributes,
                                                                classifier_member_vnf_index_ref, classifier_vnfd_id_ref,
                                                                classifier_vnfd_connection_point_ref)
                list_classifier.append(classifier_instance)
            vnffgd_instance = osm_schema.Vnffgd(vnffgd_id, vnffgd_name, vnffgd_short_name, vnffgd_vendor, vnffgd_description, vnffgd_version, list_rsp,
                                                list_classifier)
            list_vnffgd.append(vnffgd_instance)



def call_functions(source):
    set_general_informations(source)
    set_constituent_vnfd(source)
    set_ip_profiles(source)
    set_vld(source)
    set_vnffg(source)
