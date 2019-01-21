import json
from nameko.rpc import rpc
from nameko.rpc import RpcProxy

class MainEngineService:
    name = 'mainengine_service'

    translator_rpc = RpcProxy('translator_service')
    splitter_rpc = RpcProxy('splitter_service')
    adoptor_rpc = RpcProxy('adoptor_service')

    @rpc
    def hello_translator(self, name):
        message = self.translator_rpc.hello(name)
        return message

    @rpc
    def hello_splitter(self, name):
        message = self.splitter_rpc.hello(name)
        return message

    @rpc
    def hello_adoptor(self, name):
        message = self.adoptor_rpc.hello(name)
        return message
