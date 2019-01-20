import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http


class GatewayService:
    name = 'gateway'

    translator_rpc = RpcProxy('translator_service')
    splitter_rpc = RpcProxy('splitter_service')
    adoptor_rpc = RpcProxy('adoptor_service')

    @http('GET', '/translator/hello/<string:name>')
    def get_hello_translator(self, request, name):
        message = self.translator_rpc.hello(name)
        return json.dumps({'message': message})

    @http('GET', '/splitter/hello/<string:name>')
    def get_hello_splitter(self, request, name):
        message = self.splitter_rpc.hello(name)
        return json.dumps({'message': message})

    @http('GET', '/adoptor/hello/<string:name>')
    def get_hello_adoptor(self, request, name):
        message = self.adoptor_rpc.hello(name)
        return json.dumps({'message': message})
