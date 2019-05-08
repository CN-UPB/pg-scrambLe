import pymongo
from pprint import pprint
# import SonataUtilityFunctions as sonataUtilityFunctions
from SonataUtilityFunctions import utility
from nameko.rpc import rpc
# import SonataSplitter as splitter
from SonataSplitter import splitter
# import OsmSplitter as osmSplitter
#from OsmSplitter import osm_splitter
# import OSMUtilityFunctions as OSM_utility
#from OSMUtilityFunctions import osm_utility
#import requests
from Fetchfile import Fetchfile

reference_osm = "5c8869f4c957a9e5caf98629"  # Example reference id
reference_sonata = "5c833a400594c7824aba2714"


# def main():

class SplitterService:
    name = "splitter_service"

    @rpc
    def hello(self, param_list):
        # descriptor = requests.values.get('descriptor')

        # To fetch OSM file and to call osm splitter

        #received_file_osm  no servers found yet= Fetchfile(descriptor, "osm_nsd")  # we dont need parameters while fetching file
        #osmUtilityFunctions = osm_utility()
        #osmUtilityFunctions.get_osm_nsd(received_file_osm)
        #osmSplitter = osm_splitter(osmUtilityFunctions)

        #nsds_all = osmSplitter.split_osm()

        # To fetch Sonata file and to call sonata splitter

        vnf_sets = param_list['sets']
        received_file_sonata = param_list["descriptor"]  # Fetchfile(descriptor, "source_nsd")
        sonataUtilityFunctions = utility()
        sonataUtilityFunctions.get_data_sonata(received_file_sonata)
        sonSplitter = splitter(vnf_sets, sonataUtilityFunctions)
        nsds_all = sonSplitter.split_sonata()

        return nsds_all


# if __name__ == '__main__':
#    main()