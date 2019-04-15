.. Python Mano Wrappers documentation master file, created by
   sphinx-quickstart on Sat Apr 13 18:13:38 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python MANO Wrappers Documentation
================================================

Python MANO Wrappers (PMW) is a python wrapper around the REST API
calls of various MANOs. It is also a standardisation effort to 
unify the REST API of various MANOs by enforcing the ETSI SOL005 standard 
on API calls. This project is developed as part of the project group SCrAMbLE
at the University of Paderborn for the 5G-PICTURE project.  

PMW can be installed using pip by using the following command 

.. code-block:: bash
    
    pip install python-mano-wrappers


PMW is easy to use and well documented. Code usage examples are available
along with the function documentation.

**Example usage:**

.. code-block:: bash
    
    import wrappers

    username = "admin"
    password = "admin"
    mano = "osm"
    # mano = "sonata"
    host = "vm-hadik3r-05.cs.uni-paderborn.de"

    if mano == "osm":
        _client = wrappers.OSMClient.Auth(host)
    elif mano == "sonata":
        _client = wrappers.SONATAClient.Auth(host)

    response = _client.auth(
                username=username, password=password)

    print(response)


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Contents
==================

.. toctree::

    wrappers.CommonInterface
    wrappers.OSMClient
    wrappers.SONATAClient

