# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1@localhost/paier'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'you-will-never-guess')



# Load the environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


