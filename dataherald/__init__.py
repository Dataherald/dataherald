from dataherald.api import API
from dataherald.config import Settings, System

__settings = Settings()
__version__ = "0.0.1"


def client(settings: Settings = __settings) -> API:
    """Return a running dataherald.API instance"""

    system = System(settings)
    api = system.instance(API)
    system.start()
    return api
