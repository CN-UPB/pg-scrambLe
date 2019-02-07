import wrappers
from nameko.rpc import rpc
from nameko.web.handlers import http


class AdaptorService:
    name = "adaptor_service"

    @rpc
    def hello(self, name):
        message = "Adaptor: Hello " + name
        return message

    @rpc
    def auth(self, username, password, host, mano):

        if mano == "osm":
            _client = wrappers.OSMClient.Auth(host)
        elif mano == "sonata":
            _client = wrappers.SONATAClient.Auth(host)
        else:
            return "Error"

        response = _client.auth(username=username, password=password)
        return response


