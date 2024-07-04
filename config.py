import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    FILE_SERVER: str = os.getenv("FILE_SERVER")
    HOST=os.getenv("HOST")
    PORT=os.getenv("PORT")

settings = Settings()
