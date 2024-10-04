from . import db


class Lokasi(db.Model):
    __tablename__ = 'lokasi'

    id = db.Column(db.Integer, primary_key=True)
    nama_lokasi = db.Column(db.String(80), nullable=False) 
    kota = db.Column(db.String(100), nullable=False)  

    # Relationship
    schedules = db.relationship('Schedule', back_populates='lokasi')
