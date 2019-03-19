from __future__ import print_function
import json
import yaml
import sys
import getopt
from jsonschema import *
import pandas as pd
import pprint
import os
import pymongo
import json
import yaml
from yaml import loader, dumper
import sys
import getopt
from osmval import vnfd as vnfd_catalog
from osmval import nsd as nsd_catalog
from pyangbind.lib.serialise import pybindJSONDecoder
import logging
import networkx as nx
import errno
import event
from storage import DescriptorStorage
from until import read_descriptor_files, list_files, strip_root, build_descriptor_id
from utilities import setup

log = logging.getLogger(__name__)
evtlog = event.get_logger('validator.events')
storage= DescriptorStorage()

class validator():

    def __init__(self,source = None,translated = None):
        
        self.source = source
        self.translated = translated

    def sonata_nsd_validator(self):
        '''
            validates a sonata json against nsd schema

        '''
       
        descriptor_to_validate = self.translated
        
        if "descriptor_version" in descriptor_to_validate:
            schema = yaml.load(open("nsd-Pishahang.yml"))
            validator = Draft4Validator(schema , format_checker=FormatChecker())
            lastidx = 0
            error=[]
            for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
                lastidx = idx
                error.append( pprint.pformat(err))
            if lastidx == 0:
                return True
            else:
                return error
        else:
            schema = yaml.load(open("nsd-schema.yml"))
            validator = Draft4Validator(schema , format_checker=FormatChecker())
            lastidx = 0
            error=[]
            for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
                lastidx = idx
                error.append(pprint.pformat(err))
            if lastidx == 0:
                return True
            else:
                return error


    def sonata_vnfd_validator(self):
        '''
            validates a sonata json against vnfd schema

        '''        
        descriptor_to_validate = self.translated
        
        if "descriptor_version" in descriptor_to_validate:
            
            schema = yaml.load(open("vnfd-Pishahang.yml"))
            validator = Draft4Validator(schema , format_checker=FormatChecker())
            lastidx = 0
            
            for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
                lastidx = idx
                return pprint.pformat(err)
            
            if lastidx == 0:
                return True
        else:
            
            schema = yaml.load(open("vnfd-schema.yml"))
            validator = Draft4Validator(schema , format_checker=FormatChecker())
            lastidx = 0
            
            for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
                lastidx = idx
                return pprint.pformat(err)
            
            if lastidx == 0:
                return True

    def validate(self):
        '''
            lists out the common and missing keys between a source descriptor and its 
            reverse translated descriptor.

        '''
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        setup_obj = setup(client)

        uniques=[]
        duplicates=[]

        if 'virtual_deployment_units' in self.source:

            source_rev_trans = setup_obj.translate_to_sonata_vnfd(self.translated)
            result = pd.DataFrame(self.compare_dict(self.source,source_rev_trans),columns=['matched','missing'])
            return result
            
        elif 'network_functions' in self.source:

            source_rev_trans = setup_obj.translate_to_sonata_nsd(self.translated)
            result = pd.DataFrame(self.compare_dict(self.source,source_rev_trans),columns=['matched','missing'])
            return result

        elif 'vnfd:vnfd-catalog' in self.source:

            source_rev_trans = setup_obj.translate_to_osm_vnfd(self.translated)
            result = pd.DataFrame(self.compare_dict(self.source,source_rev_trans),columns=['matched','missing'])
            return result

        elif 'nsd:nsd-catalog' in self.source:

            source_rev_trans = setup_obj.translate_to_osm_nsd(self.translated)
            result = pd.DataFrame(self.compare_dict(self.source,source_rev_trans),columns=['matched','missing'])
            return result

    def compare_dict(self,dict1, dict2):
        '''
            compares two dictionary by matching the keys present/ absent in both of them

        '''
        if isinstance(dict1,dict) and isinstance(dict2,dict): 

            words1 = set(dict1.keys())
            words2 = set(dict2.keys())

            duplicates  = words1.intersection(words2)
            uniques = words1.difference(words2).union(words2.difference(words1))

            yield [duplicates, uniques]

            for key in duplicates:            
                for result in self.compare_dict(dict1[key],dict2[key]):
                    yield result

        elif isinstance(dict1,list) and isinstance(dict2,list): 

            if(len(dict1) == len(dict2)):

                for i in range(len(dict1)):
                    for result in  self.compare_dict(dict1[i],dict2[i]):
                        yield result  

def validate_service(nsd, vnfd):
    service = storage.create_service(nsd)
    if not service:
        evtlog.log("Invalid service descriptor",
                   "Failed to read the service descriptor of file '{}'"
                   .format(nsd),
                   nsd,
                   'evt_service_invalid_descriptor')
        return

    nsd_synatx = validate_service_syntax(nsd)
    nsd_inte = validate_service_integrity(service, vnfd)
    """ nsd_topo = validate_service_topology(service)"""
    return True


def validate_function(vnfd):
    func = storage.create_function(vnfd)
    if not func:
        evtlog.log("Invalid function descriptor",
                   "Couldn't store VNF of file '{0}'".format(vnfd),
                   vnfd,
                   'evt_function_invalid_descriptor')
        return

    vnfd_syntax = validate_function_syntax(vnfd)
    vnfd_inte = validate_function_integrity(func)
    vnfd_topo = validate_function_topology(func)
    return True


def validate_service_syntax(descriptor):
    descriptor_to_validate = descriptor
    if "descriptor_version" in descriptor_to_validate:
        schema = yaml.load(open("/home/pg-scramble/PycharmProjects/test/tng-schema/Nsd/nsd-Pishahang.yml"))
        validator = Draft4Validator(schema, format_checker=FormatChecker())
        lastidx = 0
        for idx, err in enumerate(validator.iter_errors(descriptor_to_validate), 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx, pprint(err)))
        if lastidx == 0:
            return True
    else:
        with open('/home/pg-scramble/PycharmProjects/test/tng-schema/Nsd/nsd-schema.yml', 'r') as f:
            schema = yaml.load(f)
        validator = Draft4Validator(schema, format_checker=FormatChecker())
        lastidx = 0
        for idx, err in enumerate(validator.iter_errors(descriptor_to_validate), 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx, pprint(err)))
        if lastidx == 0:
            return True

def validate_function_syntax(descriptor):
    descriptor_to_validate = descriptor
    if "descriptor_version" in descriptor_to_validate:
        with open('/home/pg-scramble/PycharmProjects/test/tng-schema/Vnfd/vnfd-pishahang.yml', 'r') as f:
            schema = yaml.load(f)
        validator = Draft4Validator(schema, format_checker=FormatChecker())
        lastidx = 0
        for idx, err in enumerate(validator.iter_errors(descriptor_to_validate), 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx, pprint(err)))
        if lastidx == 0:
            return True
    else:
        with open('/home/pg-scramble/PycharmProjects/test/tng-schema/Vnfd/vnfd-schema.yml', 'r') as f:
            schema = yaml.load(f)
        validator = Draft4Validator(schema, format_checker=FormatChecker())
        lastidx = 0
        for idx, err in enumerate(validator.iter_errors(descriptor_to_validate), 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx, pprint(err)))
        if lastidx == 0:
            return True

def validate_service_integrity(service, vnfd):
        # get referenced function descriptors (VNFDs)
    if not load_service_functions(service, vnfd):
        evtlog.log("Function not available",
                   "Failed to read service function descriptors",
                   service.id,
                   'evt_nsd_itg_function_unavailable')
        return

    # validate service function descriptors (VNFDs)
    for fid, f in service.functions.items():
        if not validate_function(f.filename):
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
    return True


def validate_function_integrity(func):
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
    return True


"""def validate_service_topology(service):
    # build service topology graph with VNF connection points
    service.graph = service.build_topology_graph(level=1, bridges=False)
    if not service.graph:
        evtlog.log("Invalid topology",
                   "Couldn't build topology graph of service '{0}'"
                   .format(service.id),
                   service.id,
                   'evt_nsd_top_topgraph_failed')
        return

    log.debug("Built topology graph of service '{0}': {1}"
              .format(service.id, service.graph.edges()))

    # write service graphs with different levels and options
    write = write_service_graphs(service)

    if nx.is_connected(service.graph):
        log.debug("Topology graph of service '{0}' is connected"
                  .format(service.id))
    else:
        evtlog.log("Disconnected topology",
                   "Topology graph of service '{0}' is disconnected"
                   .format(service.id),
                   service.id,
                   'evt_nsd_top_topgraph_disconnected')

    # check if forwarding graphs section is available
    if 'forwarding_graphs' not in service.content:
        evtlog.log("Forwarding graphs not available",
                   "No forwarding graphs available in service id='{0}'"
                   .format(service.id),
                   service.id,
                   'evt_nsd_top_fwgraph_unavailable')
        # don't enforce it (section not required)
        return True

    # load forwarding graphs
    if not service.load_forwarding_graphs():
        evtlog.log("Bad section: 'forwarding_graphs'",
                   "Couldn't load service forwarding graphs. ",
                   service.id,
                   'evt_nsd_top_badsection_fwgraph')
        return

    # analyse forwarding paths
    for fw_graph in service.fw_graphs:
        source_id = service.id + ":" + fw_graph['fg_id']

        for fw_path in fw_graph['fw_paths']:

            evtid = event.generate_evt_id()

            # check if number of connection points is odd
            if len(fw_path['path']) % 2 != 0:
                evtlog.log("Odd number of connection points",
                           "The forwarding path fg_id='{0}', fp_id='{1}' "
                           "has an odd number of connection points".
                           format(fw_graph['fg_id'], fw_path['fp_id']),
                           source_id,
                           'evt_nsd_top_fwgraph_cpoints_odd',
                           event_id=evtid,
                           detail_event_id=fw_path['fp_id'])
                fw_path['event_id'] = evtid

            fw_path['trace'] = service.trace_path_pairs(fw_path['path'])

            if any(pair['break'] is True for pair in fw_path['trace']):
                evtlog.log("Invalid forwarding path ({0} breakpoint(s))"
                           .format(sum(pair['break'] is True
                                       for pair in fw_path['trace'])),
                           "fp_id='{0}':\n{1}"
                           .format(fw_path['fp_id'],
                                   yaml.dump(
                                       service.trace_path(
                                           fw_path['path']))),
                           source_id,
                           'evt_nsd_top_fwpath_invalid',
                           event_id=evtid,
                           detail_event_id=fw_path['fp_id'])
                fw_path['event_id'] = evtid

                # skip further analysis
                return

            log.debug("Forwarding path fg_id='{0}', fp_id='{1}': {2}"
                      .format(fw_graph['fg_id'], fw_path['fp_id'],
                              fw_path['trace']))

        fpg = nx.DiGraph()
        for fw_path in fw_graph['fw_paths']:
            prev_node = None
            prev_iface = None
            pair_complete = False

            # convert 'connection point' path into vnf path
            for cp in fw_path['path']:
                # find vnf_id of connection point
                func = None
                s_cp = cp.split(':')
                if len(s_cp) == 2:
                    func = service.mapped_function(s_cp[0])
                    if not func:
                        log.error(
                            "Internal error: couldn't find corresponding"
                            " VNFs in forwarding path '{}'"
                                .format(fw_path['fp_id']))
                        return
                    node = service.vnf_id(func)

                else:
                    node = cp
                    fpg.add_node(node)

                if pair_complete:
                    if prev_node and prev_node == node:
                        evtid = event.generate_evt_id()
                        evtlog.log("Path within the same VNF",
                                   "The forwarding path fg_id='{0}', "
                                   "fp_id='{1}' contains a path within the"
                                   " same VNF id='{2}'"
                                   .format(fw_graph['fg_id'],
                                           fw_path['fp_id'],
                                           node),
                                   source_id,
                                   'evt_nsd_top_fwpath_inside_vnf',
                                   event_id=evtid,
                                   detail_event_id=fw_path['fp_id'])
                        fw_path['event_id'] = evtid

                        # reset trace
                        fw_path['trace'] = []
                        continue

                    fpg.add_edge(prev_node, node,
                                 attr_dict={'from': prev_iface,
                                            'to': cp})
                    pair_complete = False

                else:
                    if prev_node and prev_node != node:
                        evtlog.log("Disrupted forwarding path",
                                   "The forwarding path fg_id='{0}', "
                                   "fp_id='{1}' is disrupted at the "
                                   "connection point: '{2}'"
                                   .format(fw_graph['fg_id'],
                                           fw_path['fp_id'],
                                           cp),
                                   source_id,
                                   'evt_nsd_top_fwpath_disrupted',
                                   event_id=source_id)

                    pair_complete = True

                prev_node = node
                prev_iface = cp

            # remove 'path' from fw_path (not needed anymore)
            fw_path.pop('path')

        # find cycles
        complete_cycles = list(nx.simple_cycles(fpg))

        # remove 1-hop cycles
        cycles = []
        for cycle in complete_cycles:
            if len(cycle) > 2:
                cycles.append(cycle)

        # build cycles representative connection point structure
        cycles_list = []
        for cycle in cycles:
            cycle_dict = {'cycle_id': str(uuid.uuid4()), 'cycle_path': []}

            for idx, node in enumerate(cycle):
                link = {}

                if idx + 1 == len(cycle):  # at last element
                    next_node = cycle[0]
                else:
                    next_node = cycle[idx + 1]

                neighbours = fpg.neighbors(node)
                if next_node not in neighbours:
                    log.error("Internal error: couldn't find next hop "
                              "when building structure of cycle: {}"
                              .format(cycle))
                    continue

                edge_data = fpg.get_edge_data(node, next_node)
                link['from'] = edge_data['from']
                link['to'] = edge_data['to']

                cycle_dict['cycle_path'].append(link)
            cycles_list.append(cycle_dict)

        # report cycles
        if cycles_list and len(cycles_list) > 0:
            evtid = event.generate_evt_id()
            for cycle in cycles_list:
                evtlog.log("Found {0} cycle(s) (fg_id='{1}')"
                           .format(len(cycles_list), fw_graph['fg_id']),
                           "{0}"
                           .format(yaml.dump(cycle['cycle_path'],
                                             default_flow_style=False)),
                           source_id,
                           'evt_nsd_top_fwgraph_cycles',
                           event_id=evtid,
                           detail_event_id=cycle['cycle_id'])
            fw_graph['cycles'] = cycles_list
            fw_graph['event_id'] = evtid
    return True """

def validate_function_topology(func):
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
    return True

def load_service_functions(service, vnfd):


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

def find_graph_cycles(graph, node, prev_node=None, backtrace=None):
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
            return find_graph_cycles(graph, neighbor, prev_node=node, backtrace=backtrace)

        return backtrace


def write_service_graphs(service):
    graphsdir = 'graphs'
    try:
        os.makedirs(graphsdir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(graphsdir):
            pass

    service.build_topology_graph(level=3, bridges=False)


    for lvl in range(0, 4):
        g = service.build_topology_graph(level=lvl, bridges=False)
        for node in g.nodes():
            convert(g.node[node])
        for edge in g.edges():
            convert(g[edge[0]][edge[1]])
        nx.write_graphml(g, os.path.join(graphsdir,
                                         "{0}-lvl{1}.graphml"
                                         .format(service.id, lvl)))
        g = service.build_topology_graph(level=lvl, bridges=True)
        nx.write_graphml(g, os.path.join(graphsdir,
                                         "{0}-lvl{1}-br.graphml"
                                         .format(service.id, lvl)))

    g = service.build_topology_graph(level=3, bridges=True,
                                     vdu_inner_connections=False)
    service.complete_graph = nx.generate_graphml(g, encoding='utf-8',
                                                 prettyprint=True)
    nx.write_graphml(g, os.path.join(graphsdir,
                                     "{0}-lvl3-complete.graphml"
                                     .format(service.id)))

def convert(data):
    for key in list(data.keys()):
        val = data[key]
        if isinstance(val, datetime):
            data[key] = val.strftime(ISO8601_DATETIME)
        if isinstance(val, type(None)):
            del data[key] 
