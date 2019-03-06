""" Common Interface - auth

Reference interface to implement REST API Wrappers
for MANO Frameworks Defined according to the
ETSI GS NFV-SOL 005  V2.4.1 (2018-02). 

Defines abstract methods which are to be implemented
by the wrappers.
"""

from abc import ABC, abstractmethod

class CommonInterfaceAuth(ABC):

    @abstractmethod
    def auth(self):
        """ Authorization API

        Implement a POST method which returns an 
        authorization token to be used by other calls. 
        """
        pass
