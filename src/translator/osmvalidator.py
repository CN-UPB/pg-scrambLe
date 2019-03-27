from __future__ import print_function
import json
import yaml
from yaml import loader, dumper
import sys
import getopt
from osmdata import vnfd as vnfd_catalog
from osmdata import nsd as nsd_catalog
from pyangbind.lib.serialise import pybindJSONDecoder
from jsonschema import *
import pprint
import os
from md5 import file

"""
Tests the format of OSM VNFD and NSD descriptors
"""
__author__ = "Alfonso Tierno, Guillermo Calvino"
__date__ = "2018-04-16"
__version__ = "0.0.1"
version_date = "Apr 2018"


def remove_prefix(desc, prefix):
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
                remove_prefix(v, prefix)
            if isinstance(k, str) and k.startswith(prefix) and k != prefix:
                prefixed_list.append(k)
        for k in prefixed_list:
            desc[k[prefix_len:]] = desc.pop(k)
    elif isinstance(desc, (list, tuple)):
        for i in desc:
            if isinstance(desc, (list, tuple, dict)):
                remove_prefix(i, prefix)


def osm_validator(descriptor):
    input_file_name = descriptor
    try:
        data = input_file_name
        if "vnfd:vnfd-catalog" in data or "vnfd-catalog" in data:
            descriptor = "VNF"
            # Check if mgmt-interface is defined:
            remove_prefix(data, "vnfd:")
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



