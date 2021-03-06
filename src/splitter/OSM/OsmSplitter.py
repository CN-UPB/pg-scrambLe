import OSM.OsmSchema

class osm_splitter():

    def __init__(self, vnf_sets, utility=None):
        self.utilityFunctions = utility
        self.NSDs = []
        self.network_function_sets = vnf_sets

    """
    -vnf_index: index of the vnf which identifies a vnf.
    Returns the complete object of VNF with all its properties.
    """
    def get_network_function_object(self,vnf_index):
        for nf_object in self.utilityFunctions.list_constituent_vnfd:
            if str(nf_object.member_vnf_index) == vnf_index:
                return nf_object
        return None

    """
    -virtual_link_elan: virtual link of type ELAN
    -nsd_vl: NSD
    Returns virtual link object
    """
    def handle_elan_links(self, virtual_link_elan, nsd_vl):
        vld_instance = OsmSchema.Vld(virtual_link_elan.id, virtual_link_elan.name, virtual_link_elan.short_name,
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

    """
    Splits the network function set to create sub NSDs. All other properties are left empty.
    """
    def split_network_function(self):
        for network_function_set in self.network_function_sets:
            sub_nsd = OsmSchema.Nsd("", "", "", "", "", "", "", [], [], [], [], [])
            network_function_list = []
            for network_function in network_function_set:
                network_function_list.append(self.get_network_function_object(network_function))
            sub_nsd.ConstituentVnfd = network_function_list
            self.NSDs.append(sub_nsd)

    """
    gets list of ip_profiles objects and sets it in the sub NSDs.
    """
    def set_ip_profiles(self):
        for i in range(len(self.network_function_sets)):
            nsd_ip_profiles = self.NSDs[i]
            nsd_ip_profiles.ip_profiles = self.utilityFunctions.list_ip_profiles
            self.NSDs[i] = nsd_ip_profiles

    """
    Sets the general information which are common to all NSDs.
    """
    def set_general_information(self):
        for i in range(len(self.network_function_sets)):
            nsd_general_info = self.NSDs[i]
            nsd_general_info.id = self.utilityFunctions.id
            nsd_general_info.name = self.utilityFunctions.name
            nsd_general_info.short_name = self.utilityFunctions.short_name
            nsd_general_info.description = self.utilityFunctions.description
            nsd_general_info.vendor = self.utilityFunctions.vendor
            nsd_general_info.version = self.utilityFunctions.version
            nsd_general_info.logo = self.utilityFunctions.logo
            self.NSDs[i] = nsd_general_info

    """
    method splits the virtual links as per the sub NSDs created
    """
    def split_vld(self):
        for i in range(len(self.NSDs)):
            nsd_vld = self.NSDs[i]
            for virtual_link in self.utilityFunctions.list_vld:
                if virtual_link.type == "ELAN":
                    virtual_link_inner = self.handle_elan_links(virtual_link, nsd_vld)
                    nsd_vld.vld.append(virtual_link_inner)
            self.NSDs[i] = nsd_vld

    """
    method splits the forwarding path as per the sub NSDs created.
    """
    def split_forwarding_path(self):
        if len(self.utilityFunctions.list_vnffgd) is not 0:
            for i in range(len(self.NSDs)):
                nsd_fg = self.NSDs[i]
                for fg in self.utilityFunctions.list_vnffgd:
                    vnffgd_instance = OsmSchema.Vnffgd(fg.id, fg.name, fg.short_name, fg.vendor, fg.description, fg.version, [], [])
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
                self.NSDs[i] = nsd_fg

    """
    Creates a document for each sub NSDs
    """
    def create_files(self):
        all_nsds=[]
        for i in range(len(self.NSDs)):
            data = {}

            constituent_vnfds = {}
            constituent_vnfds['constituent-vnfd'] = []
            for constituent_vnfd in self.NSDs[i].ConstituentVnfd:
                constituent_vnfds['constituent-vnfd'].append({
                    "member-vnf-index": str(constituent_vnfd.member_vnf_index),
                    "vnfd-id-ref": str(constituent_vnfd.vnfd_id_ref)
                })

            for k in constituent_vnfds.keys():
                for constituent_vnfds_k in constituent_vnfds[k]:
                    for k_data in constituent_vnfds_k.keys():
                        if not constituent_vnfds_k[k_data] or constituent_vnfds_k[k_data] == 'None':
                            del constituent_vnfds_k[k_data]

            dns_server = {}
            dns_server['dns-server'] = []
            for ip_profile_data in self.NSDs[i].ip_profiles:
                dns_server['dns-server'].append({
                    "address": str(ip_profile_data.ip_profile_params.dns_server[0].address),
                    "address": str(ip_profile_data.ip_profile_params.dns_server[1].address)
                })

            for k in dns_server.keys():
                for dns_server_k in dns_server[k]:
                    for k_data in dns_server_k.keys():
                        if not dns_server_k[k_data] or dns_server_k[k_data] == 'None':
                            del dns_server_k[k_data]

            dhcp_params = {}
            dhcp_params['dhcp-params'] = []
            for ip_profile_data in self.NSDs[i].ip_profiles:
                dhcp_params['dhcp-params'].append({
                    "count": str(ip_profile_data.ip_profile_params.dhcp_params[0].count),
                    "start-address": str(ip_profile_data.ip_profile_params.dhcp_params[0].start_address)
                })

            for k in dhcp_params.keys():
                for dhcp_params_k in dhcp_params[k]:
                    for k_data in dhcp_params_k.keys():
                        if not dhcp_params_k[k_data] or dhcp_params_k[k_data] == 'None':
                            del dhcp_params_k[k_data]

            ip_profile_params = {}
            ip_profile_params['ip-profile-params'] = []
            for ip_profile_data in self.NSDs[i].ip_profiles:
                ip_profile_params['ip-profile-params'].append({
                    "gateway-address": str(ip_profile_data.ip_profile_params.gateway_address),
                    "ip-version": str(ip_profile_data.ip_profile_params.ip_version),
                    "subnet-address": str(ip_profile_data.ip_profile_params.subnet_address),
                    "dns-server": dns_server['dns-server'],
                    "dhcp-params": dhcp_params['dhcp-params']
                })

            for k in ip_profile_params.keys():
                for ip_profile_params_k in ip_profile_params[k]:
                    for k_data in ip_profile_params_k.keys():
                        if not ip_profile_params_k[k_data] or ip_profile_params_k[k_data] == 'None':
                            del ip_profile_params_k[k_data]

            ip_profile = {}
            ip_profile['ip-profiles'] = []
            for ip_profile_data in self.NSDs[i].ip_profiles:
                ip_profile['ip-profiles'].append({
                    "name": str(ip_profile_data.name),
                    "description": str(ip_profile_data.description),
                    "ip-profile-params": ip_profile_params['ip-profile-params']
                })

            for k in ip_profile.keys():
                for ip_profile_k in ip_profile[k]:
                    for k_data in ip_profile_k.keys():
                        if not ip_profile_k[k_data] or ip_profile_k[k_data] == 'None':
                            del ip_profile_k[k_data]

            vnfd_connection_point_ref = {}
            vnfd_connection_point_ref['vnfd-connection-point-ref'] = []
            for vnfd_connection_point_ref_data in self.NSDs[i].vld[0].vnfd_connection_point_ref_vld:
                vnfd_connection_point_ref['vnfd-connection-point-ref'].append({
                    "member-vnf-index-ref": str(vnfd_connection_point_ref_data.member_vnf_index_ref),
                    "vnfd-id-ref": str(vnfd_connection_point_ref_data.vnfd_id_ref),
                    "vnfd-connection-point-ref": str(vnfd_connection_point_ref_data.vnfd_connection_point_ref)
                })

            for k in vnfd_connection_point_ref.keys():
                for vnfd_connection_point_ref_k in vnfd_connection_point_ref[k]:
                    for k_data in vnfd_connection_point_ref_k.keys():
                        if not vnfd_connection_point_ref_k[k_data] or vnfd_connection_point_ref_k[k_data] == 'None':
                            del vnfd_connection_point_ref_k[k_data]

            vld = {}
            vld['vld'] = []
            for vld_data in self.NSDs[i].vld:
                vld['vld'].append({
                    "id": str(vld_data.id),
                    "name": str(vld_data.name),
                    "short-name": str(vld_data.short_name),
                    "type": str(vld_data.type),
                    "ip-profile-ref": str(vld_data.ip_profile_ref),
                    "vnfd-connection-point-ref": vnfd_connection_point_ref['vnfd-connection-point-ref']
                })

            for k in vld.keys():
                for vld_k in vld[k]:
                    for k_data in vld_k.keys():
                        if not vld_k[k_data] or vld_k[k_data] == 'None':
                            del vld_k[k_data]

            match_attributes = {}
            match_attributes['match-attributes'] = []
            for vnffgd_data in self.NSDs[i].vnffgd:
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
            for k in match_attributes.keys():
                for match_attributes_k in match_attributes[k]:
                    for k_data in match_attributes_k.keys():
                        if not match_attributes_k[k_data] or match_attributes_k[k_data] == 'None':
                            del match_attributes_k[k_data]

            classifier = {}
            classifier['classifier'] = []
            for vnffgd_data in self.NSDs[i].vnffgd:
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

            for k in classifier.keys():
                for classifier_k in classifier[k]:
                    for k_data in classifier_k.keys():
                        if not classifier_k[k_data] or classifier_k[k_data] == 'None':
                            del classifier_k[k_data]

            rsp = {}
            rsp['rsp'] = []
            for vnffgd_data in self.NSDs[i].vnffgd:
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

            for k in rsp.keys():
                for rsp_k in rsp[k]:
                    for k_data in rsp_k.keys():
                        if not rsp_k[k_data] or rsp_k[k_data] == 'None':
                            del rsp_k[k_data]

            vnffgd = {}
            vnffgd['vnffgd'] = []
            if bool(classifier):
                for vnffgd_data in self.NSDs[i].vnffgd:
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
                for vnffgd_data in self.NSDs[i].vnffgd:
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

            for k in vnffgd.keys():
                for vnffgd_k in vnffgd[k]:
                    for k_data in vnffgd_k.keys():
                        if not vnffgd_k[k_data] or vnffgd_k[k_data] == 'None':
                            del vnffgd_k[k_data]

            general_information = {}
            general_information['nsd'] = []
            general_information['nsd'].append({
                "id": str(self.NSDs[i].id) + "_" + str(i),
                "name": str(self.NSDs[i].name),
                "short-name": str(self.NSDs[i].short_name),
                "description": str(self.NSDs[i].description),
                "vendor": str(self.NSDs[i].vendor),
                "version": str(self.NSDs[i].version),
                "logo": str(self.NSDs[i].logo),
                "constituent-vnfd": constituent_vnfds['constituent-vnfd'],
                "ip-profiles": ip_profile['ip-profiles'],
                "vld": vld['vld'],
                "vnffgd": vnffgd['vnffgd']
            })

            for k in general_information.keys():
                for general_information_k in general_information[k]:
                    for k_data in general_information_k.keys():
                        if not general_information_k[k_data] or general_information_k[k_data] == 'None':
                            del general_information_k[k_data]

            data['nsd:nsd-catalog'] = {
                "nsd": general_information['nsd']
            }
            all_nsds.append(data)
            
        return all_nsds

    """
    Calls all functions splitting the NSD.
    """
    def split_osm(self):
        self.split_network_function()
        self.set_ip_profiles()
        self.split_vld()
        self.split_forwarding_path()
        self.set_general_information()
        return self.create_files()
