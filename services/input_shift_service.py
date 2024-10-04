# services/input_shift_service.py
from models import db
from models.shift_model import Schedule

def insert_shift(form_data):
    nama = form_data['nama']
    jabatan = form_data['jabatan']
    lokasi_id = form_data['lokasi_id']
    tanggal = form_data['tanggal']
    shift = form_data['shift']

    new_shift = Schedule(
        nama=nama,
        jabatan=jabatan,
        lokasi_id=lokasi_id,
        tanggal=tanggal,
        shift=shift
    )

    db.session.add(new_shift)
    db.session.commit()

def get_all_shifts():
    return Schedule.query.all()

def delete_shift_by_id(shift_id):
    shift = Schedule.query.get(shift_id)
    if shift:
        db.session.delete(shift)
        db.session.commit()
    else:
        raise ValueError("Shift tidak ditemukan.")

def update_shift(shift_data):
    shift_id = shift_data['id']
    shift = Schedule.query.get(shift_id)

    if not shift:
        raise ValueError("Shift tidak ditemukan.")

    # Update data shift
    shift.nama = shift_data['nama']
    shift.jabatan = shift_data['jabatan']
    shift.lokasi_id = shift_data['lokasi']
    shift.tanggal = shift_data['tanggal']
    shift.shift = shift_data['shift']

    db.session.commit()
