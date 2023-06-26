import dataherald.config
from dataherald.config import Settings, System
import logging
from dataherald.api import API
from dataherald.smart_cache.in_memory import InMemoryCache

__settings = Settings()
__version__ = "0.0.1"





def Client(settings: Settings = __settings) -> API:
    """Return a running dataherald.API instance"""

    system = System(settings)
    api = system.instance(API)
    system.start()
    return api