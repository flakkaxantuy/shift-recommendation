from flask_sqlalchemy import SQLAlchemy
from . import db


class BKO(db.Model):
    __tablename__ = 'bko'
    id = db.Column(db.Integer, primary_key=True)
    lokasi_id = db.Column(db.Integer, db.ForeignKey('lokasi.id'), nullable=False)
    shift = db.Column(db.String(10), nullable=False)
    jumlah_personil = db.Column(db.Integer, nullable=False)
    harga_satuan = db.Column(db.Float, nullable=False)
    satuan = db.Column(db.String(20), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    personil = db.Column(db.String(200), nullable=False)
    
    lokasi = db.relationship('Lokasi', backref=db.backref('bkos', lazy=True))
