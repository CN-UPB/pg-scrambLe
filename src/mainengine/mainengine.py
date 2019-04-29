import json
from nameko.rpc import rpc
from nameko.rpc import RpcProxy

class MainEngineService:
    name = 'mainengine_service'

    translator_rpc = RpcProxy('translator_service')
    splitter_rpc = RpcProxy('splitter_service')
    adaptor_rpc = RpcProxy('adaptor_service')

    @rpc
    def hello_translator(self, name):
        message = self.translator_rpc.hello(name)
        return message

    @rpc
    def hello_splitter(self, name):
        message = self.splitter_rpc.hello(name)
        return message

    @rpc
    def hello_adaptor(self, name):
        message = self.adaptor_rpc.hello(name)
        return message

    @rpc
    def adaptor_auth(self, username, password, mano):
        message = self.adaptor_rpc.hello(name)
        return message