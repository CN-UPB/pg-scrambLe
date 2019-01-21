from nameko.rpc import rpc

class AdaptorService:
    name = "adaptor_service"

    @rpc
    def hello(self, name):
        message = "Adaptor: Hello " + name
        return message