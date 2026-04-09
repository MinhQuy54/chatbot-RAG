import logging

from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="RAG chatbot",
    description="Chatbot support seeking product",
    version="1.0.0"
    )
@app.get("/")
def test():
    return {
        "status" : "online",
        "message" : "Welcome to my chatbot"
    }
logger.info("Run server completed")
