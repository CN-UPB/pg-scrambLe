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

    @http('GET', '/splitter/hello/<string:name>')
    def get_hello_splitter(self, request, name):
        message = self.mainengine_rpc.hello_splitter(name)
        return json.dumps({'message': message})

    @http('GET', '/adoptor/hello/<string:name>')
    def get_hello_adoptor(self, request, name):
        message = self.mainengine_rpc.hello_adoptor(name)
        return json.dumps({'message': message})
