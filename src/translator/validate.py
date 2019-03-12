from __future__ import print_function
import json
import yaml
import sys
import getopt
import osm_im.vnfd as vnfd_catalog
import osm_im.nsd as nsd_catalog
from pyangbind.lib.serialise import pybindJSONDecoder
from jsonschema import *
import pprint
import os
import pymongo
from utilities import setup


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
        # Open files
        file_name = input_file_name
        with open(file_name, 'r') as f:
            descriptor_str = f.read()
        file_name = None

        if input_file_name.endswith('.yaml') or input_file_name.endswith('.yml') or not \
            (input_file_name.endswith('.json') or '\t' in descriptor_str):
            data = yaml.load(descriptor_str)
        else:   # json
            data = json.loads(descriptor_str)

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
            myvnfd = vnfd_catalog.vnfd()
            pybindJSONDecoder.load_ietf_json(data, None, None, obj=myvnfd)
            return True
        elif "nsd:nsd-catalog" in data or "nsd-catalog" in data:
            descriptor = "NS"
            mynsd = nsd_catalog.nsd()
            pybindJSONDecoder.load_ietf_json(data, None, None, obj=mynsd)
            return True
        else:
            descriptor = None
            raise KeyError("This is not neither nsd-catalog nor vnfd-catalog descriptor")

    except yaml.YAMLError as exc:
        error_pos = ""
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            error_pos = "at line:%s column:%s" % (mark.line + 1, mark.column + 1)
        print("Error loading file '{}'. yaml format error {}".format(input_file_name, error_pos), file=sys.stderr)
    except ArgumentParserError as e:
        print(str(e), file=sys.stderr)
    except IOError as e:
            print("Error loading file '{}': {}".format(file_name, e), file=sys.stderr)
    except ImportError as e:
        print ("Package python-osm-im not installed: {}".format(e), file=sys.stderr)
    except Exception as e:
        if file_name:
            print("Error loading file '{}': {}".format(file_name, str(e)), file=sys.stderr)
        else:
            if descriptor:
                print("Error. Invalid {} descriptor format in '{}': {}".format(descriptor, input_file_name, str(e)),
                      file=sys.stderr)
            else:
                print("Error. Invalid descriptor format in '{}': {}".format(input_file_name, str(e)), file=sys.stderr)


def sonata_nsd_validator(descriptor):
    descriptor_to_validate = descriptor
    if "descriptor_version" in descriptor_to_validate:
        schema = yaml.load(open("tng-schema/Nsd/nsd-Pishahang.yml"))
        validator = Draft4Validator(schema , format_checker=FormatChecker())
        lastidx = 0
        for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))
        if lastidx == 0:
            return True
    else:
        schema = yaml.load(open("tng-schema/Nsd/nsd-schema.yml"))
        validator = Draft4Validator(schema , format_checker=FormatChecker())
        lastidx = 0
        for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))
        if lastidx == 0:
            return True


def sonata_vnfd_validator(descriptor):
    descriptor_to_validate = descriptor
    if "descriptor_version" in descriptor_to_validate:
        schema = yaml.load(open("tng-schema/Vnfd/vnfd-Pishahang.yml"))
        validator = Draft4Validator(schema , format_checker=FormatChecker())
        lastidx = 0
        for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))
        if lastidx == 0:
            return True
    else:
        schema = yaml.load(open("tng-schema/Vnfd/vnfd-schema.yml"))
        validator = Draft4Validator(schema , format_checker=FormatChecker())
        lastidx = 0
        for idx , err in enumerate(validator.iter_errors(descriptor_to_validate) , 1):
            lastidx = idx
            if idx == 1:
                print("\tSCHEMA ERRORS:")
            print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))
        if lastidx == 0:
            return True

def validate(source, translated):
    received_file = source
    translated_file = translated
    if 'virtual_deployment_units' in received_file:
        var = VNFD_Translator.translate_to_sonata_vnfd(translated_file)
        file1 = yaml.load(open("received_file"))
        file2 = yaml.load(open("var"))
        words1 = set(file1.read().split())
	words2 = set(file2.read().split())
	duplicates  = words1.intersection(words2)
	uniques = words1.difference(words2).union(words2.difference(words1))
	print "Duplicates(%d):%s"%(len(duplicates),duplicates)
	print "\nUniques(%d):%s"%(len(uniques),uniques)
	config_check = sonata_vnfd_validator(translated_file)

    elif 'network_functions' in received_file:
        var = setup.translate_to_sonata(translated_file)
        file1 = yaml.load(open("received_file"))
        file2 = yaml.load(open("var"))
        words1 = set(file1.read().split())
	words2 = set(file2.read().split())
	duplicates  = words1.intersection(words2)
	uniques = words1.difference(words2).union(words2.difference(words1))
	print "Duplicates(%d):%s"%(len(duplicates),duplicates)
	print "\nUniques(%d):%s"%(len(uniques),uniques)
	config_check = sonata_nsd_validator(translated_file)

    elif 'constituent-vnfd' in received_file:
        var = VNFD_Translator.translate_to_osm_vnfd(translated_file)
        file1 = yaml.load(open("received_file"))
        file2 = yaml.load(open("var"))
        words1 = set(file1.read().split())
	words2 = set(file2.read().split())
	duplicates  = words1.intersection(words2)
	uniques = words1.difference(words2).union(words2.difference(words1))
	print "Duplicates(%d):%s"%(len(duplicates),duplicates)
	print "\nUniques(%d):%s"%(len(uniques),uniques)
	config_check = osm_validator(translated_file)

    elif 'management interface' in received_file:
        var = setup.translate_to_osm(translated_file)
        file1 = yaml.load(open("received_file"))
        file2 = yaml.load(open("var"))
        words1 = set(file1.read().split())
	words2 = set(file2.read().split())
	duplicates  = words1.intersection(words2)
	uniques = words1.difference(words2).union(words2.difference(words1))
	print "Duplicates(%d):%s"%(len(duplicates),duplicates)
	print "\nUniques(%d):%s"%(len(uniques),uniques)
	config_check = osm_validator(translated_file)
