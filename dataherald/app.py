import dataherald
import dataherald.config
from dataherald.server.fastapi import FastAPI

settings = dataherald.config.Settings()
server = FastAPI(settings)
app = server.app()
