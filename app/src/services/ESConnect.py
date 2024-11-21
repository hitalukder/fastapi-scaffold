import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from elasticsearch import Elasticsearch, ConnectionTimeout
import time
import os
import logging

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

class ESConnect:

    def __init__(self) -> None:
      self.es_url = os.environ.get("ELASTIC_URL")
      self.es_user = os.environ.get("ELASTIC_USER")
      self.es_pass = os.environ.get("ELASTIC_PASSWORD")

    def get_es_client(self):
        es_client = Elasticsearch(
           self.es_url, 
           basic_auth=(self.es_user, self.es_pass), 
           verify_certs=False,
           max_retries=10,
           retry_on_timeout=True
           ##request_timeout=10000
        )
        info = es_client.info()
        logging.info(info)
        return es_client
    
   