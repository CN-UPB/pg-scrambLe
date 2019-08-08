#########################
PMW: Python MANO Wrappers
#########################

Introduction
============

Python MANO Wrappers (PMW) is a uniform python wrapper for various 
implementations of NFV Management and Network Orchestration (MANO) REST APIs. 
This project is developed as part of the project group SCrAMbLE
at the University of Paderborn for the 5G-PICTURE project
(`GitHub <https://github.com/CN-UPB/pg-scrambLe/tree/adaptor/src/adaptor/wrappers>`_).  

PMW is easy to use and well documented. Code usage examples are available
along with the function documentation.

PMW can be installed using pip:

.. code-block:: bash
    
    pip install python-mano-wrappers


Example usage
=============

.. code-block:: bash
    
    import wrappers

    username = "admin"
    password = "admin"
    mano = "osm"
    # mano = "sonata"
    host = "osmmanodemo.com"

    if mano == "osm":
        _client = wrappers.OSMClient.Auth(host)
    elif mano == "sonata":
        _client = wrappers.SONATAClient.Auth(host)

    response = _client.auth(
                username=username, password=password)

    print(response)


Design Overview
======================

The design goal of PMW is to provide a unified, 
convenient and standards oriented access to MANO API. 

To achieve this, an Abstract Base Class 
is defined which follows the conventions from the 
ETSI GS NFV-SOL 005 (SOL005) RESTful protocols specification. 

Component Description
---------------------

CommonInterface 
+++++++++++++++

The Abstract Base Class is called "CommonInterface" and it is divided 
into different sections as per the SOL005 into the following:

+ **auth.py**: Authorization API
+ **nsd.py**: NSD Management API
+ **nsfm.py**: NS Fault Management API
+ **nslcm.py**: Lifecycle Management API
+ **nspm.py**: NS Performance Management API
+ **vnfpkgm.py**: VNF Package Management API


To add python wrapper support for a specific MANO, 
the developer should inherit the Abstract Base Class
and implement all the methods defined in the class which
are supported by the target MANO. 

.. toctree::

    wrappers.CommonInterface

SONATAClient | OSMClient 
++++++++++++++++++++++++

As a starting point, support for SONATA and OpenSource MANO (OSM) is implemented.

Methods which are implemented in the target MANO and the ones supported by PWM 
are tracked using a google sheet `here <https://docs.google.com/spreadsheets/d/113TQwp5TSo5mHDQDEg5YZrMEQ2NVUD9rhagsw5tMcUo/edit#gid=0>`_ 

Documentation and usage examples are available here.

.. toctree::

    wrappers.OSMClient
    wrappers.SONATAClient

References
==========

+ ETSI GS NFV-SOL 005 - https://www.etsi.org/deliver/etsi_gs/NFV-SOL/001_099/005/02.04.01_60/gs_NFV-SOL005v020401p.pdf

+ OSM

    + OSM NBI Project - https://osm.etsi.org/gitweb/?p=osm/NBI.git;a=tree;f=osm_nbi;hb=HEAD
    + Old OSM document - https://osm.etsi.org/wikipub/images/2/24/Osm-r1-so-rest-api-guide.pdf
    + OSM architecture - https://osm.etsi.org/wikipub/index.php/Developer_HowTo_for_RO_Module#Directory_Organization

+ Sonata

    + Sonata Gatekeeper - https://github.com/sonata-nfv/son-gkeeper/tree/master/son-gtkapi
    + Sonata Routes - https://github.com/sonata-nfv/son-gkeeper/tree/master/son-gtkapi/routes
    + Sonata Usage doc - https://github.com/sonata-nfv/son-gkeeper/wiki/Usage-documentation

TODO
====

+ Include more MANOs (OpenBaton, 5GTango..)
+ Support more versions

.. toctree::

