from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from dotenv import load_dotenv
from app.route.root import routes as root_api
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API title",
    description="API Description",
    version="1.0.1-fastapi",
    servers=[
        {
            "url": "http://localhost:3001"
        }
    ],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api-service')

load_dotenv()

# Register blueprints
app.include_router(root_api.root_api_route)

origins = [ "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=3001)