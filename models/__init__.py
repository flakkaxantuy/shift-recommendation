# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Import models here to initialize them
from models.shift_model import Schedule
from models.bko_model import BKO
from models.lokasi_model import Lokasi
