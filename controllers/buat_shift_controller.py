from flask import request, jsonify, render_template, flash, redirect, url_for
from services.input_shift_service import insert_shift, get_all_shifts, delete_shift_by_id
from services.buat_shift_service import main, get_unique_days
from datetime import datetime, timedelta

def create_shift():
    location = request.json.get('location')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    
    shifts, rabs, predictions = main(location, start_date, end_date)
    hari_list = get_unique_days()
    
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    date_range = [start_date_obj + timedelta(days=x) for x in range((end_date_obj - start_date_obj).days + 1)]
    
    return jsonify({
        'shifts': shifts,
        'rabs': rabs,
        'predictions': predictions,
        'hari_list': hari_list,
        'date_range': date_range,
        'start_date': start_date_obj,
        'end_date': end_date_obj
    })

def input_shift():
    if request.method == 'POST':
        nama = request.form['nama']
        jabatan = request.form['jabatan']
        lokasi_nama = request.form['lokasi']
        tanggal = request.form['tanggal']
        hari = request.form['hari']
        shift = request.form['shift']
        
        success, message = insert_shift(nama, jabatan, lokasi_nama, tanggal, hari, shift)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('input_shift'))
    
    shifts = get_all_shifts()
    return render_template('input_data_shift.html', shifts=shifts)

def delete_shift(shift_id):
    success, message = delete_shift_by_id(shift_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('input_shift'))