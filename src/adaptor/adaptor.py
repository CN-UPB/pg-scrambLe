import wrappers
from nameko.rpc import rpc


class AdaptorService:
    name = "adaptor_service"

    @rpc
    def hello(self, name):
        message = "Adaptor: Hello " + name
        return message

    @rpc
    def auth(self, username, password, host):
        _client = wrappers.osm.OSMClient(username, password, host)
        message = "Adaptor: Auth Token " + _client.auth_token
        return message

