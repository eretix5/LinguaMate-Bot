from abc import ABC, abstractmethod

class IQuizRepository(ABC):
    @abstractmethod
    async def get(self, user_id):
        pass
    
    @abstractmethod
    async def add(self, user_id, quiz_id):   
        pass