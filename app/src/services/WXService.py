from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class WatsonXAI:
    """
    A class to encapsulate all WatsonX AI functionality.
    """

    def __init__(self):
        """
        Initializes the WatsonXAI class by loading environment variables
        and setting up credentials.
        """
        load_dotenv()
        self.model_name = os.getenv("WX_LLM_MODEL", "meta-llama/llama-3-1-70b-instruct")
        self.project_id = os.getenv("WX_PROJECT_ID")
        self.platform = os.getenv("WX_PLATFORM")
        self.api_key = os.getenv("IBM_CLOUD_API_KEY")
        self.user_name = os.getenv("WX_USER")
        self.wx_url = os.getenv("WX_URL")
        
        # Validate environment variables
        self._validate_environment()
        
        # Initialize credentials
        self.credentials = self._initialize_credentials()

    def _validate_environment(self):
        """
        Validates required environment variables and logs warnings for missing variables.
        """
        if not self.platform or not self.api_key or not self.wx_url:
            logging.error("Required environment variables are missing. "
                          "Ensure WX_PLATFORM, IBM_CLOUD_API_KEY, and WX_URL are set.")
            raise EnvironmentError("Missing required environment variables.")
        logging.info(f"Using LLM Model: {self.model_name}")
        logging.info(f"LLM Platform: {self.platform}")

    def _initialize_credentials(self) -> Credentials:
        """
        Initializes credentials based on the platform (SaaS or On-Premise).
        """
        try:
            if self.platform.lower() == "saas":
                return Credentials(
                    url=self.wx_url,
                    api_key=self.api_key
                )
            elif self.platform.lower() == "onpremise":
                return Credentials(
                    url=self.wx_url,
                    api_key=self.api_key,
                    username=self.user_name,
                    instance_id="openshift",
                    version="5.0"
                )
            else:
                logging.error("Invalid WX_PLATFORM value. Use 'onpremise' or 'saas'.")
                raise ValueError("Invalid WX_PLATFORM value.")
        except Exception as e:
            logging.exception(f"Error initializing credentials: {e}")
            raise

    def get_model(self, 
                  decoding_method: str = "greedy", 
                  max_new_tokens: int = 2000, 
                  min_new_tokens: int = 30, 
                  temperature: float = 1.0, 
                  repetition_penalty: float = 1.0) -> ModelInference:
        """
        Returns a WatsonX AI Model object configured with the specified parameters.
        """
        model_params = {
            GenParams.DECODING_METHOD: decoding_method,
            GenParams.MIN_NEW_TOKENS: min_new_tokens,
            GenParams.MAX_NEW_TOKENS: max_new_tokens,
            GenParams.TEMPERATURE: temperature,
            GenParams.REPETITION_PENALTY: repetition_penalty,
        }

        logging.debug(f"Model parameters: {model_params}")

        return ModelInference(
            model_id=self.model_name,
            params=model_params,
            credentials=self.credentials,
            project_id=self.project_id
        )

    async def send_prompt(self, prompts: str):
        """
        Sends a prompt to the WatsonX AI model and returns the response.
        """
        try:
            model = self.get_model()
            logging.info(f"Sending request to model: {model.model_id}")
            
            # WatsonX API does not support async; use synchronous call
            response = model.generate_text(prompts)
            
            logging.info("Received response from WatsonX.")
            return response
        except Exception as e:
            logging.exception(f"Error in generating text: {e}")
            raise
