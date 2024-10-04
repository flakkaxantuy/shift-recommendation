from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app as app
from models.shift_model import Schedule
from models.lokasi_model import Lokasi
from models import db
from datetime import datetime, timedelta

input_shift_bp = Blueprint('input_shift', __name__)

@input_shift_bp.route('/input_shift', methods=['GET', 'POST'])
def input_shift():
    if request.method == 'POST':
        if request.form.get('num_entries'):
            num_entries = int(request.form['num_entries'])
            return render_template('input_data_shift.html', num_entries=num_entries)

        if request.form.get('shift_id'):
            # Edit existing shift
            shift_id = request.form['shift_id']
            schedule = Schedule.query.get_or_404(shift_id)
            schedule.nama = request.form['nama']
            schedule.jabatan = request.form['jabatan']
            schedule.lokasi_id = request.form['lokasi_id']
            schedule.tanggal = datetime.strptime(request.form['tanggal'], '%Y-%m-%d')
            schedule.shift = request.form['shift']
            db.session.commit()
            flash('Data Shift berhasil diubah!', 'success')
        else:
            # Add new shifts
            nama = request.form['nama']
            jabatan = request.form['jabatan']
            lokasi_id = request.form['lokasi_id']
            tanggal_mulai = datetime.strptime(request.form['tanggal_mulai'], '%Y-%m-%d')
            tanggal_akhir = datetime.strptime(request.form['tanggal_akhir'], '%Y-%m-%d')
            shift = request.form['shift']

            current_date = tanggal_mulai
            while current_date <= tanggal_akhir:
                new_schedule = Schedule(nama=nama, jabatan=jabatan, lokasi_id=lokasi_id, tanggal=current_date, shift=shift)
                db.session.add(new_schedule)
                current_date += timedelta(days=1)

            db.session.commit()
            flash('Data Shift berhasil ditambahkan!', 'success')
        
        return redirect(url_for('input_shift.input_shift'))

    # Handling GET request
    page = request.args.get('page', 1, type=int)
    lokasi_id = request.args.get('lokasi_id', '')
    tanggal = request.args.get('tanggal', '')
    query = Schedule.query

    # Apply filters if provided
    if lokasi_id:
        query = query.filter_by(lokasi_id=lokasi_id)
    if tanggal:
        query = query.filter_by(tanggal=datetime.strptime(tanggal, '%Y-%m-%d'))

    shifts = query.paginate(page=page, per_page=10)
    lokasis = Lokasi.query.all()
    next_num, prev_num = get_next_prev_pages(shifts)

    return render_template('input_data_shift.html', shifts=shifts, lokasis=lokasis, next_num=next_num, prev_num=prev_num, lokasi_id=lokasi_id, tanggal=tanggal)

@input_shift_bp.route('/update_shift/<int:shift_id>', methods=['POST'])
def update_shift(shift_id):
    schedule = Schedule.query.get_or_404(shift_id)
    data = request.get_json()
    schedule.nama = data['nama']
    schedule.jabatan = data['jabatan']
    schedule.lokasi_id = data['lokasi_id']
    schedule.tanggal = datetime.strptime(data['tanggal'], '%Y-%m-%d')
    schedule.shift = data['shift']
    db.session.commit()
    return jsonify({'status': 'success'})

@input_shift_bp.route('/delete_shift/<int:shift_id>', methods=['POST'])
def delete_shift(shift_id):
    schedule = Schedule.query.get_or_404(shift_id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Data Shift berhasil dihapus!', 'success')
    return redirect(url_for('input_shift.input_shift'))

@input_shift_bp.route('/submit_shifts', methods=['POST'])
def submit_shifts():
    data = request.json
    app.logger.debug('Received data: %s', data)  # Debugging log
    
    # Validate received data
    if not all(key in data for key in ('nama', 'jabatan', 'lokasi_id', 'tanggal', 'shift')):
        app.logger.error('Missing data fields in the request')
        return jsonify({"status": "error", "message": "Missing data fields"}), 400
    
    try:
        new_schedule = Schedule(
            nama=data['nama'],
            jabatan=data['jabatan'],
            lokasi_id=data['lokasi_id'],
            tanggal=datetime.strptime(data['tanggal'], '%Y-%m-%d'),
            shift=data['shift']
        )
        db.session.add(new_schedule)
        db.session.commit()
        app.logger.debug('New shift added: %s', new_schedule)  # Debugging log
        return jsonify({"status": "success"})
    except Exception as e:
        app.logger.error('Error adding shift: %s', str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

def get_next_prev_pages(shifts):
    next_num = shifts.next_num if shifts.has_next else None
    prev_num = shifts.prev_num if shifts.has_prev else None
    return next_num, prev_num
