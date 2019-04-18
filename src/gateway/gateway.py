import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http


class GatewayService:
    name = 'gateway'

    mainengine_rpc = RpcProxy('mainengine_service')
    adaptor_rpc = RpcProxy('adaptor_service')

    @http('GET', 'POST','/translator/hello/<string:name>')
    def get_hello_translator(self, request, name):
        message = self.mainengine_rpc.hello_translator(name)
        return json.dumps({'message': message})

    @http('GET', '/splitter/hello/<string:name>')
    def get_hello_splitter(self, request, name):
        message = self.mainengine_rpc.hello_splitter(name)
        return json.dumps({'message': message})

    @http('GET', '/adaptor/hello/<string:name>')
    def get_hello_adaptor(self, request, name):
        message = self.mainengine_rpc.hello_adaptor(name)
        return json.dumps({'message': message})

    @http('POST', '/adaptor/auth')
    def post_auth(self, request):
        _username = request.form["username"]
        _password = request.form["password"]
        _mano = request.form["mano"]
        _host = request.form["host"]

        message = self.adaptor_rpc.auth(username=_username, password=_password, mano=_mano, host=_host)

        return message
