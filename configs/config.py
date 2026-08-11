from dotenv import load_dotenv
from configs.paths import CONFIG_PATH
import os
import yaml

load_dotenv()


def load_config():
    '''
    This function loads the config file and it in json format
    - So that other modules can access the elements of config file.
    '''
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config

class api_keys:

    def __init__(self):    
        self.GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        self.DB_URL = os.getenv('DB_URL')
        self.MODEL_DB_URL = os.getenv('MODEL_DB_URL')

api = api_keys()


