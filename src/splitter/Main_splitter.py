import pymongo
from pprint import pprint
import SonataUtilityFunctions as sonataUtilityFunctions
import SonataSplitter as splitter
import OsmSplitter as osmSplitter
import OsmUtilityFunctions as osm_utility
import OSMUtilityFunctions as OSM_utility
from Fetchfile import Fetchfile

reference_osm = "5c8869f4c957a9e5caf98629"    #Example reference id
reference_sonata = "5c833a400594c7824aba2714"


def main():

    #To fetch OSM file and to call osm splitter

    #received_file_osm = Fetchfile(reference_osm, "osm_nsd") #we dont need parameters while fetching file
    #OSM_utility.get_osm_nsd(received_file_osm)
    #osmSplitter.split_osm()



    #to fetch Sonata file and to call sonata splitter

    received_file_sonata = Fetchfile(reference_sonata, "sonata_nsd")
    sonataUtilityFunctions.get_data_sonata(received_file_sonata)
    splitter.split_sonata()


if __name__ == '__main__':
    main()
