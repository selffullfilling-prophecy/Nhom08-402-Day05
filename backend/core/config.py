from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()
CONFIG = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "LLM": ChatOpenAI(model = os.getenv("MODEL"), temperature=0, api_key=os.getenv("OPENAI_API_KEY")) 
}
     