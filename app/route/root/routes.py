from fastapi import APIRouter, requests as request

root_api_route = APIRouter()

API_PREFIX = "/api/v1"
## This routes returns the text to SQL from a given context and a sql query
@root_api_route.get(API_PREFIX)
def root_api():
    return {
        "msg": "working!"
    }