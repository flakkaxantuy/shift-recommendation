from models import Schedule, db

def handle_insert_shift(form_data):
    try:
        new_shift = Schedule(
            nama=form_data['nama'],
            jabatan=form_data['jabatan'],
            lokasi_id=form_data['lokasi_id'],
            tanggal=form_data['tanggal'],
            shift=form_data['shift']
        )
        db.session.add(new_shift)
        db.session.commit()
        return True, "Shift berhasil ditambahkan."
    except Exception as e:
        db.session.rollback()
        return False, f"Terjadi kesalahan: {str(e)}"

def handle_get_all_shifts():
    return Schedule.query.all()

def handle_delete_shift(shift_id):
    try:
        shift = Schedule.query.get(shift_id)
        if shift:
            db.session.delete(shift)
            db.session.commit()
            return True, "Shift berhasil dihapus."
        return False, "Shift tidak ditemukan."
    except Exception as e:
        db.session.rollback()
        return False, f"Terjadi kesalahan: {str(e)}"

def handle_update_shift(shift_data):
    try:
        shift_id = shift_data['id']
        shift = Schedule.query.get(shift_id)

        if not shift:
            return False, "Shift tidak ditemukan."

        # Update data shift
        shift.nama = shift_data['nama']
        shift.jabatan = shift_data['jabatan']
        shift.lokasi_id = shift_data['lokasi_id']
        shift.tanggal = shift_data['tanggal']
        shift.shift = shift_data['shift']

        db.session.commit()
        return True, "Shift berhasil diperbarui."
    except Exception as e:
        db.session.rollback()
        return False, f"Terjadi kesalahan: {str(e)}"
