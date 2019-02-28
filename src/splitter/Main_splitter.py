import pymongo
from pprint import pprint
from Fetchfile import Fetchfile
from OsmNSDSchema import get_data
from OsmNSDSchema import osm_nsd
import UtilityFunctions as sonatafunctions

parameters = "xyz"
reference_osm = "5c72a863c1e01d191a6eeeb3"    #Example reference id
reference_sonata = "5c59c83b29ab8c1f8c6deac7"


def main():

    #To fetch OSM file and to call osm splitter

    received_file_osm = Fetchfile(reference_osm, parameters)
    get_data(received_file_osm)
    osm_nsd(received_file_osm)


    #to fetch Sonata file and to call sonata splitter

    received_file_sonata = Fetchfile(reference_sonata, parameters)
    sonatafunctions.get_data_sonata(received_file_sonata)


if __name__ == '__main__':
    main()