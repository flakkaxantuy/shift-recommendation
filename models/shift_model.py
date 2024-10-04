from . import db

class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(80), nullable=False)
    jabatan = db.Column(db.String(80), nullable=False)
    lokasi_id = db.Column(db.Integer, db.ForeignKey('lokasi.id'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(20), nullable=False)


    # Relationship
    lokasi = db.relationship('Lokasi', back_populates='schedules')
