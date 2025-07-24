from dotenv import load_dotenv
from os import getenv


load_dotenv()
SECRET_KEY: str | None = getenv('SECRET_KEY')
