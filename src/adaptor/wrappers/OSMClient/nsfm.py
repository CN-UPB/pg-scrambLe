from ..CommonInterface import CommonInterfaceNslcm
from .helpers import Helpers
import json
import requests
import tarfile


def get_nsfm_alarms(self):
    """  NS Fault Management interface - 
            Alarms

    /nsfm_alarms
        GET - Query alarms related to NS instances.

    """
    pass



def get_nsfm_alarms_alarmid(self, alarmId):
    """  NS Fault Management interface - 
            Individual alarm

    /nsfm_alarms_alarmid
        GET - Read individual alarm.

    """
    pass



def patch_nsfm_alarms_alarmid(self, alarmId):
    """  NS Fault Management interface - 
            Individual alarm

    /nsfm_alarms_alarmid
        PATCH - Acknowledge individual alarm.

    """
    pass



def get_nsfm_subscriptions(self):
    """  NS Fault Management interface - 
            Subscriptions

    /nsfm_subscriptions
        GET - Query multiple subscriptions.

    """
    pass



def post_nsfm_subscriptions(self):
    """  NS Fault Management interface - 
            Subscriptions

    /nsfm_subscriptions
        POST - Subscribe to alarms related to NSs.

    """
    pass



def get_nsfm_subscriptions_subscriptionid(self, subscriptionId):
    """  NS Fault Management interface - 
            Individual subscription

    /nsfm_subscriptions_subscriptionid
        GET - Read an individual subscription.

    """
    pass



def delete_nsfm_subscriptions_subscriptionid(self, subscriptionId):
    """  NS Fault Management interface - 
            Individual subscription

    /nsfm_subscriptions_subscriptionid
        DELETE - Terminate a subscription.

    """
    pass


    # 
    # def get_nsfm_unknown(self):
    #     """  NS Fault Management interface - 
    #             Notification endpoint

    #     /nsfm_unknown
    #         GET - Test the notification endpoint.

    #     """
    #     pass


    # 
    # def post_nsfm_unknown(self):
    #     """  NS Fault Management interface - 
    #             Notification endpoint

    #     /nsfm_unknown
    #         POST - Notify about NS alarms.

    #     """
    #     pass