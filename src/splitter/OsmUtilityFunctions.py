import OsmSchema as osm_schema


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

def osm_nsd(source):
    #print (source['nsd:nsd-catalog'])
    nsd = source[0]
    for k in nsd.keys():
        if k == "nsd:nsd-catalog":
            nsd_data1 = nsd[k]
            #print(nsd_data1)
            for keyss in nsd_data1.keys():
                #if k == "nsd":
                nsd_data2 = nsd_data1[keyss]
                #print(nsd_data2)
                nsd_data = nsd_data2[0]
                for k1 in nsd_data.keys():
                    if k1 == "connection-point":
                        connection_point = nsd_data[k1]
                        for connection_point_data in connection_point:
                            name = connection_point_data.get('name')
                            floating_ip_required = connection_point_data.get('floating-ip-required')
                            type = connection_point_data.get('type')
                            connection_point_instance = osm_schema.ConnectionPoint(name, floating_ip_required, type)
                            list_connection_point.append(connection_point_instance)
                    elif k1 == "scaling-group-descriptor":
                        scaling_group_descriptor = nsd_data[k1]
                        for scaling_group_descriptor_data in scaling_group_descriptor:
                            for k2 in scaling_group_descriptor_data.keys():
                                if k2 == "scaling-policy":
                                    scaling_policy = scaling_group_descriptor_data[k2]
                                    for scaling_policy_data in scaling_policy:
                                        for k3 in scaling_policy_data.keys():
                                            if k3 == "scaling-criteria":
                                                scaling_criteria = scaling_policy_data[k3]
                                                for scaling_criteria_data in scaling_criteria:
                                                    name = scaling_criteria_data.get('name')
                                                    scale_in_threshold = scaling_criteria_data.get('scale_in_threshold')
                                                    scale_in_relational_operation = scaling_criteria_data.get('scale-in-relational-operation')
                                                    scale_out_threshold = scaling_criteria_data.get('scale_out_threshold')
                                                    scale_out_relational_operation = scaling_criteria_data.get('scale_out_relational_operation')
                                                    ns_monitoring_param_ref = scaling_criteria_data.get('ns_monitoring_param_ref')
                                                    scaling_criteria_instance = osm_schema.ScalingCriteria(name, scale_in_threshold, scale_in_relational_operation, scale_out_threshold, scale_out_relational_operation, ns_monitoring_param_ref)
                                                    list_scaling_criteria.append(scaling_criteria_instance)
                                        name = scaling_policy_data.get('name')
                                        scaling_type = scaling_policy_data.get('scaling_type')
                                        enabled = scaling_policy_data.get('enabled')
                                        scale_in_operation_type = scaling_policy_data.get('scale_in_operation_type')
                                        scale_out_operation_type = scaling_policy_data.get('scale_out_operation_type')
                                        threshold_time = scaling_policy_data.get('threshold_time')
                                        cooldown_time = scaling_policy_data.get('cooldown_time')
                                        scaling_policy_instance = osm_schema.ScalingPolicy(name, scaling_type, enabled, scale_in_operation_type, scale_out_operation_type, threshold_time, cooldown_time, list_scaling_criteria)
                                        list_scaling_policy.append(scaling_policy_instance)
                                elif k2 == "vnfd-member":
                                    vnfd_member = scaling_group_descriptor_data[k2]
                                    for vnfd_member_data in vnfd_member:
                                        min_instance_count = vnfd_member_data.get('min-instance-count')
                                        max_instance_count = vnfd_member_data.get('max-instance-count')
                                        vnfd_member_instance = osm_schema.VnfdMember(min_instance_count, max_instance_count)
                                        list_vnfd_member.append(vnfd_member_instance)
                                elif k2 == "scaling-config-action":
                                    scaling_config_action = scaling_group_descriptor_data[k2]
                                    for scaling_config_action_data in scaling_config_action:
                                        trigger = scaling_config_action_data.get('trigger')
                                        ns_service_primitive_name_ref = scaling_config_action_data.get('ns-service-primitive-name-ref')
                                        scaling_config_action_instance = osm_schema.ScalingConfigAction(trigger, ns_service_primitive_name_ref)
                                        list_scaling_config_action.append(scaling_config_action_instance)
                            name = scaling_group_descriptor_data.get('name')
                            min_instance_count = scaling_group_descriptor_data.get('min_instance_count')
                            max_instance_count = scaling_group_descriptor_data.get('max_instance_count')
                            scaling_group_descriptor_instance = osm_schema.ScalingGroupDescriptor(name, list_scaling_policy, list_vnfd_member, min_instance_count, max_instance_count, list_scaling_config_action)
                            list_scaling_group_descriptor.append(scaling_group_descriptor_instance)
                    elif k1 == "vnffgd":
                        vnffgd = nsd_data[k1]
                        for vnffgd_data in vnffgd:
                            for k2 in vnffgd_data.keys():
                                if k2 == "rsp":
                                    rsp = vnffgd_data[k2]
                                    for rsp_data in rsp:
                                        for k3 in rsp_data.keys():
                                            if k3 == "vnfd-connection-point-ref":
                                                vnfd_connection_point_ref = rsp_data[k3]
                                                print(vnfd_connection_point_ref)
                                                if vnfd_connection_point_ref is not None:
                                                    for vnfd_connection_point_ref_data in vnfd_connection_point_ref:
                                                        member_vnf_index_ref = vnfd_connection_point_ref_data.get('member_vnf_index_ref')
                                                        order = vnfd_connection_point_ref_data.get('order')
                                                        vnfd_id_ref = vnfd_connection_point_ref_data.get('vnfd_id_ref')
                                                        vnfd_ingress_connection_point_ref = vnfd_connection_point_ref_data.get('vnfd_ingress_connection_point_ref')
                                                        vnfd_egress_connection_point_ref = vnfd_connection_point_ref_data.get('vnfd_egress_connection_point_ref')
                                                        vnfd_connection_point_ref_instance = osm_schema.VnfdConnectionPointRefVnffgd(member_vnf_index_ref, order, vnfd_id_ref, vnfd_ingress_connection_point_ref, vnfd_egress_connection_point_ref)
                                                        list_vnfd_connection_point_ref.append(vnfd_connection_point_ref_instance)
                                        id = rsp_data.get('id')
                                        name = rsp_data.get('name')
                                        rsp_instance = osm_schema.Rsp(id, name, list_vnfd_connection_point_ref)
                                        list_rsp.append(rsp_instance)
                                elif k2 == "classifier":
                                    classifier = vnffgd_data[k2]
                                    for classifier_data in classifier:
                                        for k3 in classifier_data.keys():
                                            if k3 == "match-attributes":
                                                match_attributes = classifier_data[k3]
                                                for match_attributes_data in match_attributes:
                                                    id = match_attributes_data.get('id')
                                                    ip_proto = match_attributes_data.get('ip_proto')
                                                    source_ip_address =match_attributes_data.get('source_ip_address')
                                                    destination_ip_address = match_attributes_data.get('destination_ip_address')
                                                    source_port = match_attributes_data.get('source_port')
                                                    destination_port = match_attributes_data.get('destination_port')
                                                    match_attributes_instance = osm_schema.MatchAttributes(id, ip_proto, source_ip_address, destination_ip_address, source_port, destination_port)
                                                    list_match_attributes.append(match_attributes_instance)
                                        id = classifier_data.get('id')
                                        name = classifier_data.get('name')
                                        rsp_id_ref = classifier_data.get('rsp_id_ref')
                                        member_vnf_index_ref = classifier_data.get('member_vnf_index_ref')
                                        vnfd_id_ref = classifier_data.get('vnfd_id_ref')
                                        vnfd_connection_point_ref = classifier_data.get('vnfd_connection_point_ref')
                                        classifier_instance = osm_schema.Classifier(id, name, rsp_id_ref, list_match_attributes, member_vnf_index_ref, vnfd_id_ref, vnfd_connection_point_ref)
                                        list_classifier.append(classifier_instance)
                            id = vnffgd_data.get('id')
                            name = vnffgd_data.get('name')
                            short_name = vnffgd_data.get('short_name')
                            vendor = vnffgd_data.get('vendor')
                            description = vnffgd_data.get('description')
                            version = vnffgd_data.get('id')
                            vnffgd_instance = osm_schema.Vnffgd(id, name, short_name, vendor, description, version, list_rsp, list_classifier)
                            list_vnffgd.append(vnffgd_instance)


                    elif k1 == "constituent-vnfd":
                        constituent_vnfd = nsd_data[k1]
                        for constituent_vnfd_data in constituent_vnfd:
                            member_vnf_index = constituent_vnfd_data.get('member-vnf-index')
                            vnfd_id_ref = constituent_vnfd_data.get('vnfd-id-ref')
                            start_by_default =constituent_vnfd_data.get('start-by-default')
                            #print(vnfd_id_ref)
                            constituent_vnfd_instance = osm_schema.ConstituentVnfd(member_vnf_index, start_by_default, vnfd_id_ref)
                            list_constituent_vnfd.append(constituent_vnfd_instance)
                            #print(list_constituent_vnfd)
                    elif k1 == "ip-profiles":
                        ip_profiles = nsd_data[k1]
                        for ip_profiles_data in ip_profiles:
                            for k2 in ip_profiles_data.keys():
                                if k2 == "ip-profile-params":
                                    ip_profile_params = ip_profiles_data[k2]
                                    for ip_profile_params_data in ip_profile_params:

                                        print(ip_profile_params_data)
                                        for k3 in ip_profile_params_data.keys():
                                            if k3 == "dns-server":
                                                dns_server = ip_profile_params_data[k3]
                                                for dns_server_data in dns_server:
                                                    address = dns_server_data.get('address')
                                                    dns_server_instance = osm_schema.DnsServer(address)
                                                    list_dns_server.append(dns_server_instance)
                                            elif k3 == "dhcp-params":
                                                dhcp_params = ip_profile_params_data[k3]
                                                for dhcp_params_data in dhcp_params:
                                                    enabled = dhcp_params_data.get('enabled')
                                                    start_address = dhcp_params_data.get('start-address')
                                                    count = dhcp_params_data.get('count')
                                                    print(count)
                                                    dhcp_params_instance = osm_schema.DhcpParams(enabled, start_address, count)
                                                    list_dhcp_params.append(dhcp_params_instance)

                                        gateway_address = ip_profile_params_data.get('gateway-address')
                                        ip_version = ip_profile_params_data.get('ip-version')
                                        subnet_address = ip_profile_params_data.get('subnet-address')
                                        subnet_prefix_pool = ip_profile_params_data.get('subnet-prefix-pool')
                                        security_group = ip_profile_params_data.get('security_group')
                                        ip_profile_params_instance = osm_schema.IpProfileParams(ip_version, subnet_address, gateway_address, security_group, list_dns_server, list_dhcp_params, subnet_prefix_pool)
                            name = ip_profiles_data.get('name')
                            description = ip_profiles_data.get('description')
                            ip_profiles_instance = osm_schema.IpProfiles(name, description, list_dhcp_params)
                            list_ip_profiles.append(ip_profiles_instance)

                    elif k1 =="vnf-dependency":
                        vnf_dependency = nsd_data[k1]
                        for vnf_dependency_data in vnf_dependency:
                            vnf_source_ref = vnf_dependency_data.get('vnf_source_ref')
                            vnf_depends_on_ref = vnf_dependency_data.get('vnf_depends_on_ref')
                            vnf_dependency_instance = osm_schema.VnfDependency(vnf_source_ref, vnf_depends_on_ref)
                            list_vnf_dependency.append(vnf_dependency_instance)



                    elif k1 == "vld":
                        vld = nsd_data[k1]
                        #print(vld)
                        for vld_data in vld:
                            for k2 in vld_data.keys():
                                if k2 == "vnfd-connection-point-ref":
                                    vnfd_connection_point_ref = vld_data[k2]
                                    for vnfd_connection_point_ref_data in vnfd_connection_point_ref:
                                        member_vnf_index_ref = vnfd_connection_point_ref_data.get('member-vnf-index-ref')
                                        order = vnfd_connection_point_ref_data.get('order')
                                        vnfd_id_ref = vnfd_connection_point_ref_data.get('vnfd-id-ref')
                                        vnfd_connection_point_ref = vnfd_connection_point_ref_data.get('vnfd-connection-point-ref')
                                        #print(vnfd_connection_point_ref)
                                        vnfd_connection_point_ref_instance = osm_schema.VnfdConnectionPointRef(member_vnf_index_ref, order, vnfd_id_ref, vnfd_connection_point_ref)
                                        list_vnfd_connection_point_ref.append(vnfd_connection_point_ref_instance)
                                        #print(list_vnfd_connection_point_ref)
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
                            ip_profile_ref = vld_data.get('ip_profile_ref')
                            print(vim_network_name
                                  )
                            vld_instance = osm_schema.Vld(id, name, short_name, vendor, description, version, type, root_bandwidth, leaf_bandwidth, mgmt_network, vim_network_name, ip_profile_ref, list_vnfd_connection_point_ref)
                            list_vld.append(vld_instance)
                            #print(list_vld)
                id = nsd_data.get('id')
                name = nsd_data.get('name')
                short_name = nsd_data.get('short-name')
                description = nsd_data.get('description')
                vendor = nsd_data.get('vendor')
                logo = nsd_data.get('logo')
                version = nsd_data.get('version')
                nsd_data_instance = osm_schema.Nsd(id, name, short_name, description, vendor, version, logo, list_constituent_vnfd, list_vld, list_connection_point, list_scaling_group_descriptor, list_vnffgd)
                list_nsd.append(nsd_data_instance)
            #print(list_nsd)