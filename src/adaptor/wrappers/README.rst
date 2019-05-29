Python MANO Wrappers
=====================

**Python MANO Wrappers (PMW)** is a python wrapper around the REST API
calls of various MANOs. It is also a standardisation effort to 
unify the REST API of various MANOs by enforcing the ETSI SOL005 standard 
on API calls. This project is developed as part of the project group SCrAMbLE
at the University of Paderborn for the 5G-PICTURE project.  

Documentation is available here - `ReadtheDocs <https://python-mano-wrappers.readthedocs.io/en/adaptor/>`_.

**Example usage:**

.. code-block:: bash
    
    import wrappers

    username = "admin"
    password = "admin"
    mano = "osm"
    # mano = "sonata"
    host = "manosonatademo.com"

    if mano == "osm":
        _client = wrappers.OSMClient.Auth(host)
    elif mano == "sonata":
        _client = wrappers.SONATAClient.Auth(host)

    response = _client.auth(
                username=username, password=password)

    print(response)
