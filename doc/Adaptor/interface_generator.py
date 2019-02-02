# {
#     "section": "",
#     "resourceName": "",
#     "endpoint": "",
#     "methods": [
#         {
#             "method": "",
#             "meaning": ""
#         },
#         {
#             "method": "",
#             "meaning": ""
#         }
#     ]
# }

a = '''
@abstractmethod
def {0}_{1}(self):
    """ {2} - 
            {3}

    /{1}
        {4}

    """
    pass
'''

etsi = [
    
    {
        "section": "NSD Management interface",
        "resourceName": "PNF Descriptors",
        "endpoint": "pnf_descriptors",
        "methods": [
            {
                "method": "get",
                "meaning": "GET - Query information about multiple PNF descriptor resources."
            },
            {
                "method": "post",
                "meaning": "POST - Create a new PNF descriptor resource."
            }
        ]
    }, {
        "section": "NSD Management interface",
        "resourceName": "Individual PNF Descriptor",
        "endpoint": "pnf_descriptors/pnfdinfoid",
        "methods": [
            {
                "method": "get",
                "meaning": "GET - Read an individual PNFD resource."
            },
            {
                "method": "patch",
                "meaning": "PATCH - Modify the user defined data of an individual PNF descriptor resource."
            },
            {
                "method": "delete",
                "meaning": "DELETE - Delete an individual PNF descriptor resource."
            }
        ]
    }, {
        "section": "NSD Management interface",
        "resourceName": "PNFD Content",
        "endpoint": "pnf_descriptors/pnfdinfoid/pnfd_content",
        "methods": [
            {
                "method": "get",
                "meaning": "GET - Fetch the content of a PNFD."
            },
            {
                "method": "put",
                "meaning": "PUT - Upload the content of a PNFD."
            }



        ]
    }, {
        "section": "NSD Management interface",
        "resourceName": "Subscriptions",
        "endpoint": "subscriptions",
        "methods": [
            {
                "method": "get",
                "meaning": "GET - Query multiple subscriptions."
            },
            {
                "method": "post",
                "meaning": "POST - Subscribe to NSD and PNFD change notifications."
            }
        ]
    }, {
        "section": "NSD Management interface",
        "resourceName": "Individual Subscription",
        "endpoint": "subscriptions/subscriptionId",
        "methods": [
            {
                "method": "get",
                "meaning": "GET - Read an individual subscription resource"
            },
            {
                "method": "delete",
                "meaning": "DELETE - Terminate a subscription."
            }
        ]
    }
    ]

for i in etsi:
    for m in i["methods"]:
        _section = i["section"]
        _method = m["method"]
        _meaning = m["meaning"]
        _resourceName = i["resourceName"]
        _endpoint = i["endpoint"]
        print(a.format(_method, _endpoint, _section, _resourceName, _meaning))
        print("\n")




 
