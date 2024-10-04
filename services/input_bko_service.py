from app import db
from models.bko_model import BKO
from sqlalchemy.exc import IntegrityError

def insert_bko(tanggal, lokasi, shift, jumlah_personil, harga_satuan, satuan, event, personil):
    try:
        new_bko = BKO(
            tanggal=tanggal,
            lokasi=lokasi,
            shift=shift,
            jumlah_personil=jumlah_personil,
            harga_satuan=harga_satuan,
            satuan=satuan,
            event=event,
            personil=personil
        )
        db.session.add(new_bko)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def fetch_all_bko():
    return BKO.query.all()

def delete_bko(id):
    bko = BKO.query.get(id)
    if not bko:
        return False

    try:
        db.session.delete(bko)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def update_bko(bko_data):
    try:
        bko_id = bko_data['id']
        bko = BKO.query.get(bko_id)

        if not bko:
            return False

        bko.tanggal = bko_data['tanggal']
        bko.lokasi = bko_data['lokasi']
        bko.shift = bko_data['shift']
        bko.jumlah_personil = bko_data['jumlah_personil']
        bko.harga_satuan = bko_data['harga_satuan']
        bko.satuan = bko_data['satuan']
        bko.event = bko_data['event']
        bko.personil = bko_data['personil']

        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
