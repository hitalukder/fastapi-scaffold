import asyncio
import os
import json
import time
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Security
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.LLMInput import LLMInput
from app.src.model.LLMOutput import LLMOutput
from app.src.services.PromptService import build_prompt
from app.src.services.WXService import WatsonXAI
from ibm_watsonx_ai.foundation_models import Model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Load environment variables
load_dotenv()

# Initialize router
llm_api_route = APIRouter(
    prefix="/api/v1/llm",
    tags=["LLM API"]
)

# API Key header
API_KEY_NAME = "LLM_REST_API_KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Token limits
MAX_TOKEN_LIMIT = int(os.environ.get("MAX_TOKEN_LIMIT", 7000))
MIN_TOKEN_LIMIT = int(os.environ.get("MIN_TOKEN_LIMIT", 6000))

# WatsonX Service
watsonx_model_service = WatsonXAI()


# Utility functions
def validate_api_key(api_key: str) -> bool:
    """Validate API key from headers."""
    return api_key == os.environ.get("LLM_REST_API_KEY")


async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """Retrieve and validate the API key."""
    if validate_api_key(api_key_header):
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Invalid API credentials."
    )


def build_context() -> str:
    """Stub for building context; replace with actual retriever logic."""
    return ""


# Routes
@llm_api_route.post("/generate", description="Generate LLM response using WatsonX library")
async def generate_text(
    llm_input: LLMInput, 
    api_key: str = Security(get_api_key)
) -> LLMOutput:
    """
    Endpoint to generate text response using WatsonX AI.
    """
    question = llm_input.query.strip()
    info = {}

    try:
        # Generate prompt
        context = build_context()
        llm_input_prompt = build_prompt(question, context)

        # LLM generation
        tic = time.perf_counter()
        llm_response = await watsonx_model_service.send_prompt(llm_input_prompt)
        info["llm-generation"] = time.perf_counter() - tic

        logging.info(json.dumps(info, indent=4))
        return LLMOutput(response=llm_response)
    except Exception as e:
        logging.error(f"Failed to generate LLM response: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate LLM response."
        )


@llm_api_route.post("/stream", description="Stream LLM response")
async def stream_response(
    llm_input: LLMInput, 
    api_key: str = Security(get_api_key)
) -> StreamingResponse:
    """
    Endpoint to stream LLM responses in real-time.
    """
    question = llm_input.query.strip()

    try:
        # Generate prompt
        context = build_context()
        llm_input_prompt = build_prompt(question, context)
        watsonx_model = watsonx_model_service.get_model()

        # Stream response
        return StreamingResponse(
            event_stream(watsonx_model, llm_input_prompt),
            media_type="text/event-stream"
        )
    except Exception as e:
        logging.error(f"Error during stream generation: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate stream."
        )


async def event_stream(watsonx_model: Model, llm_input: str):
    """
    Generator function for event streaming.
    """
    try:
        tic = time.perf_counter()
        count = 0

        for chunk in watsonx_model.generate_text_stream(prompt=llm_input, raw_response=True):
            if count == 0:
                logging.info(f"Time for first token: {time.perf_counter() - tic:.2f}s")
            count += 1

            if chunk["results"][0]["stop_reason"] == "eos_token":
                logging.info(f"Time for last token: {time.perf_counter() - tic:.2f}s")

            yield f"data: {json.dumps(chunk)}\n\n"  # SSE format
    except (BrokenPipeError, ConnectionResetError) as e:
        logging.error(f"Streaming error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connection error during streaming."
        )
    except Exception as e:
        logging.error(f"General streaming error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
