from configs.config import api
from langchain_groq import ChatGroq

class LLM:
    def __init__(self):
        self.gpt_20b = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        api_key=api.GROQ_API_KEY
        )

        self.llama_70b = ChatGroq(

            model = "llama-3.3-70b-versatile",
            temperature=0,
            api_key=api.GROQ_API_KEY
        )
    
llm = LLM()