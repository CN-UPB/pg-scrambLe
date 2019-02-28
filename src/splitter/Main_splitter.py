import pymongo
from pprint import pprint
from Fetchfile import Fetchfile
from OSMNSDallschema import get_data
from OSMNSDallschema import osm_nsd
parameters = "xyz"
reference = "5c72a863c1e01d191a6eeeb3"    #Example reference id


def main():

    received_file = Fetchfile(reference, parameters)
    get_data(received_file)
    osm_nsd(received_file)

if __name__ == '__main__':
    main()