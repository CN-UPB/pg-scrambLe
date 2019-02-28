from jsonschema import *
import pprint
import json
import os
import yaml

if os.path.exists("tng-schema/vnfd/vnfd-schema.yml"):
    schema = yaml.load(open("tng-schema/vnfd/vnfd-schema.yml"))
if os.path.exists("sonata_vnfd.yml"):
    vnfd = yaml.load(open("sonata_vnfd.yml"))
if os.path.exists("tng-schema/Nsd/nsd-schema.yml"):
    schema1 = yaml.load(open("tng-schema/Nsd/nsd-schema.yml"))
if os.path.exists("sonata_nsd.yml"):
    nsd = yaml.load(open("sonata_nsd.yml"))


def valid(schema, inst):
    validator = Draft4Validator(schema, format_checker=FormatChecker())
    lastidx = 0
    for idx, err in enumerate(validator.iter_errors(inst) , 1):
        lastidx = idx
        if idx == 1:
            print("\tSCHEMA ERRORS:")
        print("\t{0}. {1}\n".format(idx , pprint.pformat(err)))

    if lastidx == 0:
        print("\tVALIDATED SUCCESS")



valid(schema,vnfd)
valid(schema1, nsd)