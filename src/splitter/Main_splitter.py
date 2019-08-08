from Sonata.SonataUtilityFunctions import Utility
from nameko.rpc import rpc
from Sonata.SonataSplitter import splitter

class SplitterService:
    name = "splitter_service"

    @rpc
    def split(self, param_list):

        try:
            '''To fetch Sonata file and to call sonata splitter'''
            # fetches the set of VNFs to split.
            vnf_sets = param_list['sets']
            # fetches the descriptor
            received_file_sonata = param_list["descriptor"]

            # Pulls out information from the received sonata NSD file and stores it in variables.
            sonataUtilityFunctions = Utility(received_file_sonata)
            sonSplitter = splitter(vnf_sets, sonataUtilityFunctions)
            # Splits the NSD in parts as per the VNF set and returns it to the plugin.
            nsds_all = sonSplitter.split_sonata()
            return nsds_all
        except LookupError:
            print("No descriptor/ sets found.")
        except:
            print("Unknown Error!")
