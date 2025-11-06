from PackWrapper.Logger import Logger
from functools import wraps

class ExtensionLogger:
    
    class ID:
        
        _id: str | None = None
        
        @classmethod
        def set(cls, id):
            
            if Logger.ID.get() is None:
                Logger.ID.set(f"{id}")
            else:
                cls._id = id
                Logger.ID.set(f"{Logger.ID.get()} | {id}")
        
        @classmethod
        def get(cls):
            return cls._id

        @classmethod
        def reset(cls):
            if Logger.ID.get() is not None:
                Logger.ID.set(str(Logger.ID.get()).split(" | ")[0])
            else:
                cls._id = None
        
        def __init__(self, id: str | None = None):
            self.__id = id
        
        def __call__(self, func): 
            @wraps(func)
            def wrapper(*args, **kwargs):           
                self.set(self.__id)
                result = func(*args, **kwargs)
                self.reset()
                return result
            return wrapper
