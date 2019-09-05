from abc import ABC, abstractmethod


class CommonInterfaceDatabase(ABC):
    

    @abstractmethod
    def get_mano_list(self):
        
        pass

    @abstractmethod
    def post_mano_create(self):
        
        pass

      
    @abstractmethod
    def post_mano_remove(self):
        
        pass
        