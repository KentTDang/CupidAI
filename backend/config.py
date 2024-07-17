import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
