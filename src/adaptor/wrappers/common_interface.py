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

    ###########################
    # NSD Management Interfaces

    # Base: {apiRoot}/nsd/v1
    ###########################

    @abstractmethod
    def get_ns_descriptors(self):
        """ NSD Management Interface - NS Descriptors

        /ns_descriptors
            GET - Query information about multiple
                    NS descriptor resources.
        """
        pass

    @abstractmethod
    def post_ns_descriptors(self):
        """ NSD Management Interface - NS Descriptors

        /ns_descriptors
            POST - Create a new NS descriptor resource.
        """
        pass

    @abstractmethod
    def get_ns_descriptors_nsd_content(self, nsdInfoId):
        """ NSD Management Interface - Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}
            GET - Fetch the content of NSD
        """
        pass

    @abstractmethod
    def patch_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}
            PATCH - Modify the operational state and/or 
                the user defined data of an individual
                NS descriptor resource.
        """
        pass

    @abstractmethod
    def delete_ns_descriptors(self):
        """ NSD Management Interface - Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}
            DELETE - Delete the content of NSD
        """
        pass

    @abstractmethod
    def put_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - NSD Content
        
        /ns_descriptors/{nsdInfoId}/nsd_c
            PUT - Upload the content of NSD
        """
        pass



    ###################################
    # VNF Package Management Interfaces

    # Base: {apiRoot}/vnfpkgm/v1
    ###################################

    @abstractmethod
    def get_vnf_packages(self):
        """ VNF Package Management Interface - VNF packages

        /vnf_packages
            GET - Query VNF packages information

        """
        pass

    @abstractmethod
    def post_vnf_packages(self):
        """ VNF Package Management Interface - VNF packages

        /vnf_packages
            POST - Create a new individual 
                    VNFpackage resource

        """
        pass

    @abstractmethod
    def get_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Individual VNF package

        /vnf_packages/{vnfPkgId}
            GET - Read information about an 
                    individual VNF package
   
        """
        pass

    @abstractmethod
    def patch_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Individual VNF package

        /vnf_packages/{vnfPkgId}
        PATCH - Update information about an
                    individual VNF package

        """
        pass

    @abstractmethod
    def delete_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Individual VNF package

        /vnf_packages/{vnfPkgId}
            DELETE - Delete an individual VNF package

        """
        pass

    @abstractmethod
    def get_vnf_packages_vnfpkgid_vnfd(self, vnfPkgId):
        """ VNF Package Management Interface - 
                VNFD of an individual VNF package

        /vnf_packages/{vnfPkgId}/vnfd
            GET - Read VNFD of an on-boarded VNF package
   
        """
        pass

    @abstractmethod
    def get_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
                VNF package content

        /vnf_packages/{vnfPkgId}/package_content
            GET - Fetch an on-boarded VNF package
   
        """
        pass

    @abstractmethod
    def put_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
                VNF package content

        /vnf_packages/{vnfPkgId}/package_content
            PUT - Upload a VNF package by providing 
                    the content of the VNF package
   
        """
        pass

    @abstractmethod
    def post_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
                Upload VNF package from URI task

        /vnf_packages/{vnfPkgId}/package_content/upload_from_uri
            POST - Upload a VNF package by providing
                    the address information of the VNF package
   
        """
        pass

    @abstractmethod
    def get_vnf_packages_vnfpkgid_artifacts_artifactpath(self, 
            vnfPkgId, artifactPath):
        """ VNF Package Management Interface - 
                Individual VNF package artifact

        /vnf_packages/{vnfPkgId}/artifacts/{artifactPath}
            GET - Fetch individual VNF package artifact
   
        """
        pass

    @abstractmethod
    def get_vnf_packages_subscriptions(self):
        """ VNF Package Management Interface - 
                Subscriptions

        /subscriptions
            GET - Query multiple subscriptions
   
        """
        pass

    @abstractmethod
    def post_vnf_packages_subscriptions(self):
        """ VNF Package Management Interface - 
                Subscriptions

        /subscriptions
            POST - Subscribe to notifications related
                to on-boarding and/or changes of VNF packages
   
        """
        pass

    @abstractmethod
    def get_pnf_descriptors(self):
        """ NSD Management interface -
                PNF Descriptors

        /pnf_descriptors
            GET - Query information about multiple
                PNF descriptor resources.

        """
        pass

    @abstractmethod
    def post_pnf_descriptors(self):
        """ NSD Management interface -
                PNF Descriptors

        /pnf_descriptors
            POST - Create a new PNF descriptor resource.

        """
        pass

    @abstractmethod
    def get_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            GET - Read an individual PNFD resource.

        """
        pass

    @abstractmethod
    def patch_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            PATCH - Modify the user defined data of an 
                        individual PNF descriptor resource.

        """
        pass

    @abstractmethod
    def delete_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
                Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid
            DELETE - Delete an individual PNF descriptor resource.

        """
        pass

    @abstractmethod
    def get_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        """ NSD Management interface -
                PNFD Content

        /pnf_descriptors/pnfdinfoid/pnfd_content
            GET - Fetch the content of a PNFD.

        """
        pass

    @abstractmethod
    def put_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        """ NSD Management interface -
                PNFD Content

        /pnf_descriptors/pnfdinfoid/pnfd_content
            PUT - Upload the content of a PNFD.

        """
        pass

    @abstractmethod
    def post_subscriptions(self, pnfdInfoId):
        """ NSD Management interface -
                Subscriptions

        /subscriptions
            POST - Subscribe to NSD and PNFD change notifications.

        """
        pass

    @abstractmethod
    def get_subscriptions(self, subscriptionId):
        """ NSD Management interface -
                Subscriptions

        /subscriptions
            GET - Query multiple subscriptions.

        """
        pass

    @abstractmethod
    def get_subscriptions_subscriptionid(self, subscriptionid):
        """ NSD Management interface -
                Individual Subscription

        /subscriptions/subscriptionId
            GET - Read an individual subscription resource

        """
        pass

    @abstractmethod
    def delete_subscriptions_subscriptionid(self, subscriptionid):
        """ NSD Management interface -
                Individual Subscription

        /subscriptions/subscriptionId
            DELETE - Terminate a subscription.

        """
        pass

