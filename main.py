import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
#from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api-service")

# Environment variable fallback
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:3001")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# FastAPI application instance
app = FastAPI(
    title="API Title",
    description="API Description",
    version="1.0.1-fastapi",
    servers=[{"url": SERVER_URL}],
)

# Register routes
from app.route.root import routes as root_api
app.include_router(root_api.root_api_route)
from app.route.llm import routes as llm_api
app.include_router(llm_api.llm_api_route)


# Middleware for trusted hosts
# TRUSTED_HOSTS = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Update environment variable for flexibility
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start logging
logger.info("Starting API service...")

# Application entry point
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3001, log_level="info")
