from nameko.rpc import rpc

class AdoptorService:
    name = "adoptor_service"

    @rpc
    def hello(self, name):
        message = "Adoptor: Hello " + name
        return message