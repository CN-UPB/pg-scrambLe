import yaml

list_vnfd_connection_point_ref = []
list_vld = []
list_constituent_vnfd = []
list_nsd = []
list_dns_server = []
list_dhcp_params = []

def osm_nsd():
    nsd = source['nsd:nsd-catalog']
    #print (nsd)
    for k in nsd.keys():
        if k == "nsd":
            nsd_data = nsd[k]
            print(nsd_data)
            for nsd_data1 in nsd_data:
                for k1 in nsd_data1.keys():
                    if k1 == "constituent-vnfd":
                        constituent_vnfd = nsd_data1[k1]
                        for constituent_vnfd_data in constituent_vnfd:
                            member_vnf_index = constituent_vnfd_data['member-vnf-index']
                            vnfd_id_ref = constituent_vnfd_data.get('vnfd-id-ref')
                            start_by_default =constituent_vnfd_data.get('start-by-default')
                           # print(vnfd_id_ref)
                            constituent_vnfd_instance = ConstituentVnfd(member_vnf_index, start_by_default, vnfd_id_ref)
                            list_constituent_vnfd.append(constituent_vnfd_instance)
                            print(list_constituent_vnfd)
                    elif k1 == "ip-profiles":
                        ip_profiles = nsd_data1[k1]
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
                                                    dns_server_instance = DnsServer(address)
                                                    list_dns_server.append(dns_server_instance)
                                            elif k3 == "dhcp-params":
                                                dhcp_params = ip_profile_params_data[k3]
                                                for dhcp_params_data in dhcp_params:
                                                    enabled = dhcp_params_data.get('enabled')
                                                    start_address = dhcp_params_data.get('start-address')
                                                    count = dhcp_params_data.get('count')
                                                    print(count)
                                                    dhcp_params_instance = DhcpParams(enabled, start_address, count)
                                                    list_dhcp_params.append(dhcp_params_instance)

                                        gateway_address = ip_profile_params_data.get('gateway-address')
                                        ip_version = ip_profile_params_data.get('ip-version')
                                        subnet_address = ip_profile_params_data.get('subnet-address')
                                        subnet_prefix_pool = ip_profile_params_data.get('subnet-prefix-pool')



                    elif k1 == "vld":
                        vld = nsd_data1[k1]
                        for vld_data in vld:
                            for k2 in vld_data.keys():
                                if k2 == "vnfd-connection-point-ref":
                                    vnfd_connection_point_ref = vld_data[k2]
                                    for vnfd_connection_point_ref_data in vnfd_connection_point_ref:
                                        member_vnf_index_ref = vnfd_connection_point_ref_data['member-vnf-index-ref']
                                        order = vnfd_connection_point_ref_data.get('order')
                                        vnfd_id_ref = vnfd_connection_point_ref_data['vnfd-id-ref']
                                        vnfd_connection_point_ref = vnfd_connection_point_ref_data['vnfd-connection-point-ref']
                                        #print(vnfd_connection_point_ref)
                                        vnfd_connection_point_ref_instance = VnfdConnectionPointRef(member_vnf_index_ref, order, vnfd_id_ref, vnfd_connection_point_ref)
                                        list_vnfd_connection_point_ref.append(vnfd_connection_point_ref_instance)
                                       # print(list_vnfd_connection_point_ref)
                            id = vld_data['id']
                            name = vld_data['name']
                            short_name = vld_data['short-name']
                            type = vld_data['type']
                            mgmt_network = vld_data.get('mgmt-network')
                            vim_network_name = vld_data.get('vim-network-name')
                            #print(mgmt_network)
                            vld_instance = Vld(id, name, short_name, type, mgmt_network, vim_network_name, list_vnfd_connection_point_ref)
                            list_vld.append(vld_instance)
                            #print(list_vld)
                id = nsd_data1['id']
                name = nsd_data1['name']
                short_name = nsd_data1['short-name']
                description = nsd_data1['description']
                vendor = nsd_data1['vendor']
                logo = nsd_data1['logo']
                version = nsd_data1['version']
                nsd_data_instance = Nsd(id, name, short_name, description, vendor, version, logo, list_constituent_vnfd, list_vld)
                list_nsd.append(nsd_data_instance)
                print(list_nsd)

        #for k in parameters.keys():
         #   print(k)
         #   if k == "nsd":
          #      nsd_data = data[k]
           #     print(nsd_data)



class NsdNsdCatalog:
    nsd = []
    def __init__(self, nsd):
        self.nsd = nsd

class Nsd:
    id = ""
    name = ""
    short_name = ""
    description = ""
    vendor = ""
    version = "" #optional
    logo = "" #optional
    ConstituentVnfd = []
    vld = []
    ip_profiles = []

    def __init__(self,id, name, short_name, description, vendor, version, logo, ConstituentVnfd, vld):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.description = description
        self.vendor = vendor
        self.version = version
        self.logo = logo
        self.ConstituentVnfd = ConstituentVnfd
        self.vld = vld

class ConstituentVnfd:  #complete
    member_vnf_index = ""
    start_by_default = ""
    vnfd_id_ref = ""

    def __init__(self, member_vnf_index, start_by_default, vnfd_id_ref):
        self.member_vnf_index = member_vnf_index
        self.start_by_default = start_by_default
        self.vnfd_id_ref = vnfd_id_ref

class IpProfiles:
    name = ""
    description = ""
    ip_profile_params = []
    def __init__(self, name, description, ip_profile_params):
        self.name = name
        self.description = description
        self.ip_profile_params = ip_profile_params

class IpProfileParams: #complete
    gateway_address = 0
    ip_version = ""
    subnet_address = ""
    security_group = ""
    dns_server = []
    dhcp_params = []
    subnet_prefix_pool = ""

    def __init__(self, gateway_address, ip_version, subnet_address, security_group):
        self.gateway_address = gateway_address
        self.ip_version = ip_version
        self.subnet_address = subnet_address
        self.security_group = security_group
        self.dns_server = dns_server
        self.dhcp_params = dhcp_params
        self.subnet_prefix_pool = subnet_prefix_pool

class DnsServer:
    address = ""
    def __init__(self, address):
        self.address = address

class DhcpParams:
    enabled = ""
    start_address = ""
    count = ""
    def __init__(self, enabled, start_address, count):
        self.enabled = enabled
        self.start_address = start_address
        self.count = count


class Vld:
    id = ""
    name = ""
    short_name = ""   #optional
    type = ""
    mgmt_network = ""
    vim_network_name = ""  #optional
    vnfd_connection_point_ref = []

    def __init__(self, id, name, short_name, type, mgmt_network, vim_network_name, vnfd_connection_point_ref):
        self.id = id
        self.name = name
        self.short_name = short_name
        self.type = type
        self.mgmt_network = mgmt_network
        self.vim_network_name = vim_network_name
        self.vnfd_connection_point_ref = vnfd_connection_point_ref


class VnfdConnectionPointRef:   #complete --- vnfd_connection_point_ref is in 2 names :vnfd_ingress_connection_point_ref and vnfd_egress_connection_point_ref
    member_vnf_index_ref = ""
    order = "" #
    vnfd_id_ref = ""
    vnfd_connection_point_ref = ""

    def __init__(self, member_vnf_index_ref, order, vnfd_id_ref, vnfd_connection_point_ref):
        self.member_vnf_index_ref = member_vnf_index_ref
        self.order = order
        self.vnfd_id_ref = vnfd_id_ref
        self.vnfd_connection_point_ref = vnfd_connection_point_ref

    # def __init__(self, member-vnf-index-ref, vnfd-id-ref, vnfd-connection-point-ref):
    #   self.






def get_data():
    with open('D:\Paderborn\project\Implementation\OsmVnfd\hackfest_sfc_ns\hackfest_sfc_nsd.yaml', "r") as incoming_file:
        data = yaml.load(incoming_file)
        #print(data)
    return data

source = get_data()
osm_nsd()