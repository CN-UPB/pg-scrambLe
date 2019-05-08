import wrappers
import json

from nameko.rpc import rpc
from nameko.web.handlers import http

API_VERSION = "v1"

class AdaptorService:
    name = "adaptor_service"

    @rpc
    def hello(self, name):
        message = "Adaptor: Hello " + name
        return message

    @http('POST', '/adaptor/{}/auth'.format(API_VERSION))
    def post_auth(self, request):
        username = request.form["username"]
        password = request.form["password"]
        mano = request.form["mano"]
        host = request.form["host"]

        if mano == "osm":
            _client = wrappers.OSMClient.Auth(host)
        elif mano == "sonata":
            _client = wrappers.SONATAClient.Auth(host)
        else:
            return "Error"

        response = _client.auth(
                        username=username, password=password)
        return response

    @http('GET', '/adaptor/{}/nsd/ns_descriptors'.format(API_VERSION))
    def get_ns_descriptors(self, request):
        mano = request.form["mano"]
        host = request.form["host"]
        token = request.form["token"]

        if mano == "osm":
            _client = wrappers.OSMClient.Nsd(host)
        elif mano == "sonata":
            _client = wrappers.SONATAClient.Nsd(host)
        else:
            return "Error"

        response = _client.get_ns_descriptors(token=token)
        return response

    @http('POST', '/adaptor/{}/nsd/ns_descriptors'.format(API_VERSION))
    def post_ns_descriptors(self, request):
        mano = request.form["mano"]
        host = request.form["host"]
        token = request.form["token"]
        package = request.files['nsd']

        if mano == "osm":
            _client = wrappers.OSMClient.Nsd(host)
        elif mano == "sonata":
            _client = wrappers.SONATAClient.Nsd(host)
        else:
            return "Error"

        package_path = '/tmp/' + package.filename
        package.save(package_path)
        response = _client.post_ns_descriptors(
                        token=token, package_path=package_path)
        return response


    @http('GET', '/adaptor/{}/vnfpkgm/vnf_packages'.format(API_VERSION))
    def get_vnf_packages(self, request):
        mano = request.form["mano"]
        host = request.form["host"]
        token = request.form["token"]

        if mano == "osm":
            _client = wrappers.OSMClient.VnfPkgm(host)
        elif mano == "sonata":
            _client = wrappers.SONATAClient.VnfPkgm(host)
        else:
            return "Error"

        response = _client.get_vnf_packages(token=token)
        return response


    @http('POST', '/adaptor/{}/vnfpkgm/vnf_packages'.format(API_VERSION))
    def post_vnf_packages(self, request):
        mano = request.form["mano"]
        host = request.form["host"]
        token = request.form["token"]
        package = request.files['vnfd']

        if mano == "osm":
            _client = wrappers.OSMClient.VnfPkgm(host)
        elif mano == "sonata":
            _client = wrappers.SONATAClient.VnfPkgm(host)
        else:
            return "Error"

        package_path = '/tmp/' + package.filename
        package.save(package_path)

        response = _client.post_vnf_packages(
                        token=token, package_path=package_path)
        return response


    @http('GET', '/adaptor/{}/nslcm/ns_instances'.format(API_VERSION))
    def get_ns_instances(self, request):
        mano = request.form["mano"]
        host = request.form["host"]
        token = request.form["token"]

        if mano == "osm":
            _client = wrappers.OSMClient.Nslcm(host)
        elif mano == "sonata":
            _client = wrappers.SONATAClient.Nslcm(host)
        else:
            return "Error"

        response = _client.get_ns_instances(token=token)
        return response


    @http('POST', '/adaptor/{}/nslcm/ns_instances/instantiate'.format(API_VERSION))
    def post_ns_instances_nsinstanceid_instantiate(self, request):
        mano = request.form["mano"]
        host = request.form["host"]
        token = request.form["token"]
        options = json.loads(request.form["options"])

        if mano == "osm":
            _client = wrappers.OSMClient.Nslcm(host)
            response = _client.post_ns_instances_nsinstanceid_instantiate(
                            token=token, 
                            nsDescription= options['nsDescription'],
                            nsName = options['nsName'],
                            nsdId = options['nsdId'],
                            vimAccountId = options['vimAccountId'])

        elif mano == "sonata":
            _client = wrappers.SONATAClient.Nslcm(host)
            response = _client.post_ns_instances_nsinstanceid_instantiate(
                            token=token, 
                            nsInstanceId= options['nsInstanceId'],
                            egresses = options['egresses'],
                            ingresses = options['ingresses'],
                            )

        else:
            return "Error"

        return response


    @http('POST', '/adaptor/{}/nslcm/ns_instances/terminate'.format(API_VERSION))
    def post_ns_instances_nsinstanceid_terminate(self, request):
        mano = request.form["mano"]
        host = request.form["host"]
        token = request.form["token"]
        options = json.loads(request.form["options"])

        if mano == "osm":
            _client = wrappers.OSMClient.Nslcm(host)
            response = _client.post_ns_instances_nsinstanceid_terminate(
                        token=token, id=options['nsInstanceId'])
        elif mano == "sonata":
            _client = wrappers.SONATAClient.Nslcm(host)
            response = _client.post_ns_instances_nsinstanceid_terminate(
                        token=token, nsInstanceId=options['nsInstanceId'])

        else:
            return "Error"


        return response

