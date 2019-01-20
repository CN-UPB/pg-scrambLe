from nameko.rpc import rpc

class TranslatorService:
    name = "translator_service"

    @rpc
    def hello(self, name):
        message = "Translator: Hello " + name
        return message