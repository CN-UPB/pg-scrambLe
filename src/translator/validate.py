import json
import yaml
import pandas as pd
import sys
import getopt
from jsonschema import *
import pprint
import os
import pymongo
from utilities import setup

### @Vivek
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
            
            schema = yaml.load(open("vnfd-Pishahang.yml"))
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
            result = pd.DataFrame(self.compare_dict(self.source,source_rev_trans,'root'),columns=['matched','missing','key'])
            return result
            
        elif 'network_functions' in self.source:

            source_rev_trans = setup_obj.translate_to_sonata_nsd(self.translated)
            result = pd.DataFrame(self.compare_dict(self.source,source_rev_trans,'root'),columns=['matched','missing','key'])
            return result

        elif 'vnfd:vnfd-catalog' in self.source:

            source_rev_trans = setup_obj.translate_to_osm_vnfd(self.translated)
            result = pd.DataFrame(self.compare_dict(self.source,source_rev_trans,'root'),columns=['matched','missing','key'])
            return result

        elif 'nsd:nsd-catalog' in self.source:

            source_rev_trans = setup_obj.translate_to_osm_nsd(self.translated)
            result = pd.DataFrame(self.compare_dict(self.source,source_rev_trans,'root'),columns=['matched','missing','key'])
            return result

    ### @Arka
    def compare_dict(self,dict1, dict2, keys=''):
        '''
            compares two dictionary by matching the keys present/ absent in both of them

        '''
        if isinstance(dict1,dict) and isinstance(dict2,dict): 

            words1 = set(dict1.keys())
            words2 = set(dict2.keys())

            matched  = words1.intersection(words2)
            missing = words1.difference(words2).union(words2.difference(words1))

            yield [matched, missing,keys]

            for key in matched:            
                for result in self.compare_dict(dict1[key],dict2[key],key):
                    yield result

        elif isinstance(dict1,list) and isinstance(dict2,list): 

            if(len(dict1) == len(dict2)):

                for i in range(len(dict1)):
                    for result in  self.compare_dict(dict1[i],dict2[i],keys):
                        yield result   