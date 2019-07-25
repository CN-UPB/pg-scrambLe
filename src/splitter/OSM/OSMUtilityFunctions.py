import OsmSchema


class OsmUtility:
    
    def __init__(self):
    
        self.id = ""
        self.name = ""
        self.short_name = ""
        self.description = ""
        self.vendor = ""
        self.version = ""
        self.logo = ""

        self.list_vnfd_connection_point_ref = []
        self.list_vld = []
        self.list_constituent_vnfd = []
        self.list_nsd = []
        self.list_dns_server = []
        self.list_dhcp_params = []
        self.list_connection_point = []
        self.list_scaling_criteria = []
        self.list_scaling_policy = []
        self.list_vnfd_member = []
        self.list_scaling_config_action = []
        self.list_scaling_group_descriptor = []
        self.list_rsp = []
        self.list_match_attributes = []
        self.list_classifier = []
        self.list_vnffgd = []
        self.list_vnf_dependency = []
        self.list_ip_profiles = []

    '''Gets the osm NSD and calls utility functions'''
    def get_osm_nsd(self, received_file_osm):
        source = received_file_osm
        try:
            for key in source.keys():
                if key == "nsd:nsd-catalog":
                    nsd = source[key]
                    for nsd_key in nsd.keys():
                        nsd_temp = nsd[nsd_key]
                        self.call_functions(nsd_temp[0])
        except KeyError:
            print("One or more key not found!")

    '''Pulls the information specific to the whole NSD and stores it in variables.'''
    def set_general_information(self, source):
        try:
            self.name = source.get('name')
            self.id = source.get('id')
            self.short_name = source.get('short-name')
            self.description = source.get('description')
            self.vendor = source.get('vendor')
            self.version = source.get('version')
            self.logo = source.get('logo')
        except KeyError:
            print("One or more key not found!")

    '''Pulls out all the VNFs and stores it in a list'''
    def set_constituent_vnfd(self, source):
        try:
            constituent_vnfd = source['constituent-vnfd']
            for constituent_vnfd_data in constituent_vnfd:
                member_vnf_index = constituent_vnfd_data.get('member-vnf-index')
                vnfd_id_ref = constituent_vnfd_data.get('vnfd-id-ref')
                start_by_default = constituent_vnfd_data.get('start-by-default')
                constituent_vnfd_instance = OsmSchema.ConstituentVnfd(member_vnf_index, start_by_default, vnfd_id_ref)
                self.list_constituent_vnfd.append(constituent_vnfd_instance)
        except KeyError:
            print("One or more key not found!")

    '''Pulls out information related to ip-profile and stores it in a list of ip profiles'''
    def set_ip_profiles(self, source):
        try:
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
                        dns_server_instance = OsmSchema.DnsServer(address)
                        self.list_dns_server.append(dns_server_instance)

                    dhcp_params = ip_profile_params.get('dhcp-params')
                    enabled = dhcp_params.get('enabled')
                    start_address = dhcp_params.get('start-address')
                    count = dhcp_params.get('count')
                    dhcp_params_instance = OsmSchema.DhcpParams(enabled, start_address, count)
                    self.list_dhcp_params.append(dhcp_params_instance)

                    ip_profile_params_instance = OsmSchema.IpProfileParams(ip_version, subnet_address, gateway_address,
                                                                            security_group, self.list_dns_server,
                                                                            self.list_dhcp_params, subnet_prefix_pool)
                    ip_profiles_instance = OsmSchema.IpProfiles(name, description, ip_profile_params_instance)
                    self.list_ip_profiles.append(ip_profiles_instance)
        except KeyError:
            print("One or more key not found!")

    '''Pulls virtual link descriptor information and stores it in a list of vld'''
    def set_vld(self, source):
        try:
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
                    vnfd_connection_point_ref_instance = OsmSchema.VnfdConnectionPointRef(member_vnf_index_ref, order,
                                                                                           vnfd_id_ref,
                                                                                           vnfd_connection_point_ref)
                    self.list_vnfd_connection_point_ref.append(vnfd_connection_point_ref_instance)

                vld_instance = OsmSchema.Vld(id, name, short_name, vendor, description, version, type, root_bandwidth,
                                              leaf_bandwidth, mgmt_network, vim_network_name, ip_profile_ref,
                                              self.list_vnfd_connection_point_ref)
                self.list_vld.append(vld_instance)
        except KeyError:
            print("One or more key not found!")

    '''Pulls graph related information from the NSD and stores it in a list of graphs'''
    def set_vnffg(self, source):
        try:
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
                        rsp_instance = OsmSchema.Rsp(rsp_id, rsp_name, rsp_vnfd_connection_point_ref, rsp_member_vnf_index_ref, rsp_order, rsp_vnfd_id_ref)
                        self.list_rsp.append(rsp_instance)
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
                            match_attributes_instance = OsmSchema.MatchAttributes(match_attributes_id,
                                                                                  match_attributes_ip_proto,
                                                                                  match_attributes_source_ip_address,
                                                                                  match_attributes_destination_ip_address,
                                                                                  match_attributes_source_port,
                                                                                  match_attributes_destination_port)
                            self.list_match_attributes.append(match_attributes_instance)

                        classifier_instance = OsmSchema.Classifier(classifier_id, classifier_name, classifier_rsp_id_ref,
                                                         self.list_match_attributes,
                                                         classifier_member_vnf_index_ref, classifier_vnfd_id_ref,
                                                         classifier_vnfd_connection_point_ref)
                        self.list_classifier.append(classifier_instance)
                    vnffgd_instance = OsmSchema.Vnffgd(vnffgd_id, vnffgd_name, vnffgd_short_name, vnffgd_vendor,
                                             vnffgd_description, vnffgd_version, self.list_rsp, self.list_classifier)
                    self.list_vnffgd.append(vnffgd_instance)
        except KeyError:
            print("One or more key not found!")

    '''Calls all utility functions one after another.'''
    def call_functions(self, source):
        self.set_general_informations(source)
        self.set_constituent_vnfd(source)
        self.set_ip_profiles(source)
        self.set_vld(source)
        self.set_vnffg(source)
