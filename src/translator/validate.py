from __future__ import print_function
import json
import sys
from osmdata import vnfd as vnfd_catalog
from osmdata import nsd as nsd_catalog
from pyangbind.lib.serialise import pybindJSONDecoder
import os
import logging
import uuid
from jsonschema import *
import networkx as nx
import errno
import yaml
import event
from storage import DescriptorStorage
from until import read_descriptor_files, list_files, strip_root, build_descriptor_id
import pprint
import time

log = logging.getLogger(__name__)
evtlog = event.get_logger('validator.events')
storage = DescriptorStorage()

### @Vivek
class validator():

    def osm_validator(self,descriptor):
        if 'nsd:nsd-catalog' in descriptor:
            descriptor_to_validate = descriptor
            with open(r"osm-schema-nsd.json") as f:
                schema = json.load(f)
            v = Draft4Validator(schema, format_checker=FormatChecker())
            lastidx = 0
            for idx, err in enumerate(v.iter_errors(descriptor_to_validate), 1):
                lastidx = idx
                if idx == 1:
                    print("\tSCHEMA ERRORS:")
                print("\t{0}. {1}\n".format(idx, pprint.pformat(err)))
                print("\t{0}. {1}\n".format(idx, pprint.pformat(err.path)))
            self.osm_dep_validator(descriptor_to_validate)
            if lastidx == 0:
                return True

        elif 'vnfd:vnfd-catalog' in descriptor:
            descriptor_to_validate = descriptor
            with open(r"osm-vnfd-schema.json") as f:
                schema = json.load(f)
            v = Draft4Validator(schema , format_checker=FormatChecker())
            lastidx = 0
            for idx , err in enumerate(v.iter_errors(descriptor_to_validate) , 1):
                lastidx = idx
                if idx == 1:
                    print("\tSCHEMA ERRORS:")
                print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))
                print("\t{0}. {1}\n".format(idx , pprint.pformat(err.path)))
            self.osm_dep_validator(descriptor_to_validate)
            if lastidx == 0:
                return True
        else:
            print("This is not a valid OSM descriptor")


    def sonata_nsd_validate(self,descriptor, vnfd = None):
        if 'network_functions' and "descriptor_version" in descriptor:
            descriptor_to_validate = descriptor
            with open(r"nsd-Pishahang.yml") as f:
                schema = yaml.load(f)
            v = Draft4Validator(schema , format_checker=FormatChecker())
            lastidx = 0
            for idx , err in enumerate(v.iter_errors(descriptor_to_validate), 1):
                lastidx = idx
                if idx == 1:
                    print("\tSCHEMA ERRORS:")
                print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))
                print("\t{0}. {1}\n".format(idx , pprint.pformat(err.path)))
            if lastidx == 0:
                return True

        elif "network_functions" in descriptor:
            service = storage.create_service(descriptor)
            if not service:
                evtlog.log("Invalid service descriptor",
                           "Failed to read the service descriptor of file '{}'"
                           .format(descriptor),
                           descriptor,
                           'evt_service_invalid_descriptor')
                return
            self.validate_service_syntax(descriptor)
            if not vnfd:
                print("service integrity is not validated as there is no vnfd")
            elif vnfd != {}:
                self.validate_service_integrity(service, vnfd)
            return True
        else:
            print("This is not a valid sonata or Pishahang descriptor")


    def sonata_vnfd_validate(self,descriptor):
        if "virtual_deployment_units" and "descriptor_version" in descriptor:
            descriptor_to_validate = descriptor
            with open(r"vnfd-pishahang.yml") as f:
                schema = yaml.load(f)
            v = Draft4Validator(schema , format_checker=FormatChecker())
            lastidx = 0
            for idx , err in enumerate(v.iter_errors(descriptor_to_validate) , 1):
                lastidx = idx
                if idx == 1:
                    print("\tSCHEMA ERRORS:")
                print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))
                print("\t{0}. {1}\n".format(idx , pprint.pformat(err.path)))
            if lastidx == 0:
                return True
        elif "virtual_deployment_units" in descriptor:
            func = storage.create_function(descriptor)
            if not func:
                evtlog.log("Invalid function descriptor",
                           "Couldn't store VNF of file '{0}'".format(descriptor),
                           descriptor,
                           'evt_function_invalid_descriptor')
                return

            self.validate_function_syntax(descriptor)
            self.validate_function_integrity(func)
            self.validate_function_topology(func)
            return True
        else:
            print("This is not a valid sonata or Pishahang descriptor")


    def validate_service_syntax(self,descriptor):
        descriptor_to_validate = descriptor
        with open(r"nsd-schema.yml") as f:
            schema = yaml.load(f)
        validator = Draft4Validator(schema, format_checker=FormatChecker())
        lastidx = 0
        for idx, err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx, pprint.pformat(err)))
            print("\t{0}. {1}\n".format(idx, pprint.pformat(err.path)))
        if lastidx == 0:
            print("NSD syntax validated")
            return True


    def validate_function_syntax(self,descriptor):
        descriptor_to_validate = descriptor
        with open(r"vnfd-schema.yml") as f:
            schema = yaml.load(f)
        validator = Draft4Validator(schema , format_checker=FormatChecker())
        lastidx = 0
        for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))
            print("\t{0}. {1}\n".format(idx , pprint.pformat(err.path)))
        if lastidx == 0:
            print("VNFD syntax validated")
            return True


    def validate_service_integrity(self,service, vnfd):
            # get referenced function descriptors (VNFDs)
        if not self.load_service_functions(service, vnfd):
            evtlog.log("Function not available",
                       "Failed to read service function descriptors",
                       service.id,
                       'evt_nsd_itg_function_unavailable')
            return

        # validate service function descriptors (VNFDs)
        for fid, f in service.functions.items():
            if not self.sonata_vnfd_validate(f.filename):
                evtlog.log("Invalid function",
                           "Failed to validate function descriptor '{0}'"
                           .format(f.filename),
                           service.id,
                           'evt_nsd_itg_function_invalid')
                return

        # load service connection points
        if not service.load_connection_points():
            evtlog.log("Bad section 'connection_points'",
                       "Couldn't load the connection points of "
                       "service id='{0}'"
                       .format(service.id),
                       service.id,
                       'evt_nsd_itg_badsection_cpoints')
            return

        # load service links
        if not service.load_virtual_links():
            evtlog.log("Bad section 'virtual_links'",
                       "Couldn't load virtual links of service id='{0}'"
                       .format(service.id),
                       service.id,
                       'evt_nsd_itg_badsection_vlinks')
            return

        undeclared = service.undeclared_connection_points()
        if undeclared:
            for cxpoint in undeclared:
                evtlog.log("{0} Undeclared connection point(s)"
                           .format(len(undeclared)),
                           "Virtual links section has undeclared connection "
                           "point: {0}".format(cxpoint),
                           service.id,
                           'evt_nsd_itg_undeclared_cpoint')
            return

        # check for unused connection points
        unused_ifaces = service.unused_connection_points()
        if unused_ifaces:
            for cxpoint in unused_ifaces:
                evtlog.log("{0} Unused connection point(s)"
                           .format(len(unused_ifaces)),
                           "Unused connection point: {0}"
                           .format(cxpoint),
                           service.id,
                           'evt_nsd_itg_unused_cpoint')

        # verify integrity between vnf_ids and vlinks
        for vl_id, vl in service.vlinks.items():
            for cpr in vl.connection_point_refs:
                s_cpr = cpr.split(':')
                if len(s_cpr) == 1 and cpr not in service.connection_points:
                    evtlog.log("Undefined connection point",
                               "Connection point '{0}' in virtual link "
                               "'{1}' is not defined"
                               .format(cpr, vl_id),
                               service.id,
                               'evt_nsd_itg_undefined_cpoint')
                    return
                elif len(s_cpr) == 2:
                    func = service.mapped_function(s_cpr[0])
                    if not func or s_cpr[1] not in func.connection_points:
                        evtlog.log("Undefined connection point",
                                   "Function (VNF) of vnf_id='{0}' declared "
                                   "in connection point '{0}' in virtual link "
                                   "'{1}' is not defined"
                                   .format(s_cpr[0], s_cpr[1], vl_id),
                                   service.id,
                                   'evt_nsd_itg_undefined_cpoint')
                        return
        print("NSD integrity validated")
        return True


    def validate_function_integrity(self,func):
        if not func.load_connection_points():
            evtlog.log("Missing 'connection_points'",
                       "Couldn't load the connection points of "
                       "function id='{0}'"
                       .format(func.id),
                       func.id,
                       'evt_vnfd_itg_badsection_cpoints')
            return

        if not func.load_units():
            evtlog.log("Missing 'virtual_deployment_units'",
                       "Couldn't load the units of function id='{0}'"
                       .format(func.id),
                       func.id,
                       'evt_vnfd_itg_badsection_vdus')
            return

        if not func.load_unit_connection_points():
            evtlog.log("Bad section 'connection_points'",
                       "Couldn't load VDU connection points of "
                       "function id='{0}'"
                       .format(func.id),
                       func.id,
                       'evt_vnfd_itg_vdu_badsection_cpoints')
            return

        # load function links
        if not func.load_virtual_links():
            evtlog.log("Bad section 'virtual_links'",
                       "Couldn't load the links of function id='{0}'"
                       .format(func.id),
                       func.id,
                       'evt_vnfd_itg_badsection_vlinks')
            return

        # check for undeclared connection points
        undeclared = func.undeclared_connection_points()
        if undeclared:
            for cxpoint in undeclared:
                evtlog.log("{0} Undeclared connection point(s)"
                           .format(len(undeclared)),
                           "Virtual links section has undeclared connection "
                           "points: {0}".format(cxpoint),
                           func.id,
                           'evt_vnfd_itg_undeclared_cpoint')
            return

        # check for unused connection points
        unused_ifaces = func.unused_connection_points()
        if unused_ifaces:
            for cxpoint in unused_ifaces:
                evtlog.log("{0} Unused connection point(s)"
                           .format(len(unused_ifaces)),
                           "Function has unused connection points: {0}"
                           .format(cxpoint),
                           func.id,
                           'evt_vnfd_itg_unused_cpoint')

        # verify integrity between unit connection points and units
        for vl_id, vl in func.vlinks.items():
            for cpr in vl.connection_point_refs:
                s_cpr = cpr.split(':')
                if len(s_cpr) == 1 and cpr not in func.connection_points:
                    evtlog.log("Undefined connection point",
                               "Connection point '{0}' in virtual link "
                               "'{1}' is not defined"
                               .format(cpr, vl_id),
                               func.id,
                               'evt_nsd_itg_undefined_cpoint')
                    return
                elif len(s_cpr) == 2:
                    unit = func.units[s_cpr[0]]
                    if not unit or s_cpr[1] not in unit.connection_points:
                        evtlog.log("Undefined connection point(s)",
                                   "Invalid connection point id='{0}' "
                                   "of virtual link id='{1}': Unit id='{2}' "
                                   "is not defined"
                                   .format(s_cpr[1], vl_id, s_cpr[0]),
                                   func.id,
                                   'evt_vnfd_itg_undefined_cpoint')
                        return
        print("VNFD integrity validated")
        return True


    def validate_function_topology(self,func):
        log.info("Validating topology of function '{0}'"
                     .format(func.id))
        func.graph = func.build_topology_graph(bridges=True)
        if not func.graph:
            evtlog.log("Invalid topology graph",
                           "Couldn't build topology graph of function '{0}'"
                           .format(func.id),
                           func.id,
                           'evt_vnfd_top_topgraph_failed')
            return

        log.debug("Built topology graph of function '{0}': {1}"
                      .format(func.id, func.graph.edges()))
        print("VNFD topology validated")
        return True


    def load_service_functions(self,service, vnfd):
        # load all VNFDs
        path_vnfs = read_descriptor_files(vnfd)
        # check for errors
        if 'network_functions' not in service.content:
            log.error("Service doesn't have any functions. "
                      "Missing 'network_functions' section.")
            return

        functions = service.content['network_functions']

        # store function descriptors referenced in the service
        for func in functions:
            fid = build_descriptor_id(func['vnf_vendor'],
                                      func['vnf_name'],
                                      func['vnf_version'])
            if fid not in path_vnfs.keys():
                evtlog.log("VNF not found",
                           "Referenced function descriptor id='{0}' couldn't "
                           "be loaded".format(fid),
                           service.id,
                           'evt_nsd_itg_function_unavailable')
                return

            vnf_id = func['vnf_id']
            new_func = storage.create_function(path_vnfs[fid])

            service.associate_function(new_func, vnf_id)

        return True


    def find_graph_cycles(self,graph, node, prev_node=None, backtrace=None):
        if not backtrace:
            backtrace = []
            neighbors = graph.neighbors(node)

            if prev_node:
                neighbors.pop(neighbors.index(prev_node))
            if not len(neighbors) > 0:
                return None

            if node in backtrace:
                cycle = backtrace[backtrace.index(node):]
                return cycle
            backtrace.append(node)

            for neighbor in neighbors:
                return self.find_graph_cycles(graph, neighbor, prev_node=node, backtrace=backtrace)

            return backtrace

    """
    Tests the format of OSM VNFD and NSD descriptors
    """
    __author__ = "Alfonso Tierno, Guillermo Calvino"
    __date__ = "2018-04-16"
    __version__ = "0.0.1"
    version_date = "Apr 2018"


    def remove_prefix(self,desc, prefix):
        """
        Recursively removes prefix from keys
        :param desc: dictionary or list to change
        :param prefix: prefix to remove. Must
        :return: None, param desc is changed
        """
        prefix_len = len(prefix)
        if isinstance(desc, dict):
            prefixed_list=[]
            for k,v in desc.items():
                if isinstance(v, (list, tuple, dict)):
                    self.remove_prefix(v, prefix)
                if isinstance(k, str) and k.startswith(prefix) and k != prefix:
                    prefixed_list.append(k)
            for k in prefixed_list:
                desc[k[prefix_len:]] = desc.pop(k)
        elif isinstance(desc, (list, tuple)):
            for i in desc:
                if isinstance(desc, (list, tuple, dict)):
                    self.remove_prefix(i, prefix)


    def osm_dep_validator(self,descriptor):
        input_file_name = descriptor
        try:
            data = input_file_name
            if "vnfd:vnfd-catalog" in data or "vnfd-catalog" in data:
                descriptor = "VNF"
                # Check if mgmt-interface is defined:
                self.remove_prefix(data, "vnfd:")
                vnfd_descriptor = data["vnfd-catalog"]
                vnfd_list = vnfd_descriptor["vnfd"]
                mgmt_iface = False
                for vnfd in vnfd_list:
                    vdu_list = vnfd["vdu"]
                    for vdu in vdu_list:
                        interface_list = []
                        external_interface_list = vdu.pop("external-interface", ())
                        for external_interface in external_interface_list:
                            if external_interface.get("virtual-interface", {}).get("type") == "OM-MGMT":
                                raise KeyError(
                                    "Wrong 'Virtual-interface type': Deprecated 'OM-MGMT' value. Please, use 'PARAVIRT' instead")
                        interface_list = vdu.get("interface", ())
                        for interface in interface_list:
                            if interface.get("virtual-interface", {}).get("type") == "OM-MGMT":
                                raise KeyError(
                                    "Wrong 'Virtual-interface type': Deprecated 'OM-MGMT' value. Please, use 'PARAVIRT' instead")
                    if vnfd.get("mgmt-interface"):
                        mgmt_iface = True
                        if vnfd["mgmt-interface"].get("vdu-id"):
                            raise KeyError("'mgmt-iface': Deprecated 'vdu-id' field. Please, use 'cp' field instead")
                if not mgmt_iface:
                    raise KeyError("'mgmt-iface' is a mandatory field and it is not defined")
                myvnfd = vnfd_catalog()
                pybindJSONDecoder.load_ietf_json(data, None, None, obj=myvnfd)
                return True
            elif "nsd:nsd-catalog" in data or "nsd-catalog" in data:
                descriptor = "NS"
                mynsd = nsd_catalog()
                pybindJSONDecoder.load_ietf_json(data, None, None, obj=mynsd)
                return True
            else:
                descriptor = None
                raise KeyError("This is not neither nsd-catalog nor vnfd-catalog descriptor")

        except Exception as e:
            if input_file_name:
                print("Error loading file: {}".format(pprint.pformat(str(e))), file=sys.stderr)
            else:
                if descriptor:
                    print("Error. Invalid {} descriptor format in '{}': {}".format(descriptor, input_file_name, str(e)),
                          file=sys.stderr)
                else:
                    print("Error. Invalid descriptor format in '{}': {}".format(input_file_name, str(e)), file=sys.stderr)