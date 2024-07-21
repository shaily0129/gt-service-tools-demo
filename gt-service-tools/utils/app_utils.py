from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler

app = FastAPI(
    title="ASU Tools",
    description="Demo of using an interactive tools ",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler("app.log", maxBytes=1000000, backupCount=1)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
