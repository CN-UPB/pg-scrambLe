""" Common Interface

Reference interface to implement REST API Wrappers
for MANO Frameworks Defined according to the
ETSI GS NFV-SOL 005  V2.4.1 (2018-02). 

Defines abstract methods which are to be implemented
by the wrappers.
"""

from abc import ABC, abstractmethod
 
class CommonInterface(ABC):

    @abstractmethod
    def auth(self):
        """ Authorization API

        Implement a POST method which returns an 
        authorization token to be used by other calls. 
        """
        pass

    @abstractmethod
    def get_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - Fetch NSD

        Fetch the content of NSD
        """
        pass

    @abstractmethod
    def put_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - Upload NSD
        
        Upload the content of NSD
        """
        pass
