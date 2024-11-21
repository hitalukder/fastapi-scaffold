from fastapi import APIRouter, requests as request
from fastapi.responses import HTMLResponse

root_api_route = APIRouter()

API_PREFIX = "/"
## This routes returns the text to SQL from a given context and a sql query
@root_api_route.get(API_PREFIX)
def root_api():
    return HTMLResponse(
        """
        <html>
                <head>
                    <title>RAG Pipeline</title>
                </head>
                <body>
                    <h1>RAG Pipeline!</h1>
                    <h3>For complete API documentation visit open API <a href="/docs">docs</a></h3>
                </body>
        </html>
        """
    )