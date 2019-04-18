import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http


class GatewayService:
    name = 'gateway'

    mainengine_rpc = RpcProxy('mainengine_service')

    @http('GET', '/translator/hello/<string:name>')
    def get_hello_translator(self, request, name):
        message = self.mainengine_rpc.hello_translator(name)
        return json.dumps({'message': message})

    @http('GET', '/Main_splitter/hello/<string:descriptor>')
    def get_hello_splitter(self, request, descriptor):
        message = self.mainengine_rpc.hello_splitter(descriptor)
        return json.dumps({'message': message})

    @http('GET', '/adaptor/hello/<string:name>')
    def get_hello_adaptor(self, request, name):
        message = self.mainengine_rpc.hello_adaptor(name)
        return json.dumps({'message': message})
