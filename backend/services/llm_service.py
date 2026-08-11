from configs.config import api
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

class LLM:
    def __init__(self):
        self.mini_model_with_fallback = ChatOpenAI(
            model="gpt",
            api_key="anything",
            base_url="http://litellm:4000/v1"
        )

        self.large_model_with_fallback = ChatOpenAI(
            model="llama",
            api_key="anything",
            base_url="http://litellm:4000/v1"
        )
    


