from nameko.rpc import rpc

class SplitterService:
    name = "splitter_service"

    @rpc
    def hello(self, name):
        message = "Splitter: Hello " + name
        return message