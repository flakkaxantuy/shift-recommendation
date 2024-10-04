from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, Response
from models.bko_model import BKO
from models.lokasi_model import Lokasi
from models import db
import csv
import io

bko_bp = Blueprint('bko', __name__)

@bko_bp.route('/bko', methods=['GET', 'POST'])
def bko():
    if request.method == 'POST':
        lokasi_id = request.form.get('lokasi_id')
        shift = request.form.get('shift')
        jumlah_personil = request.form.get('jumlah_personil')
        harga_satuan = request.form.get('harga_satuan')
        satuan = request.form.get('satuan')
        event = request.form.get('event')
        personil = request.form.get('personil')

        try:
            jumlah_personil = int(jumlah_personil)
            harga_satuan = float(harga_satuan)
        except ValueError:
            flash('Jumlah personil harus berupa angka dan harga satuan harus berupa angka atau desimal.', 'danger')
            return redirect(url_for('bko.bko'))

        new_bko = BKO(
            lokasi_id=lokasi_id, 
            shift=shift, 
            jumlah_personil=jumlah_personil, 
            harga_satuan=harga_satuan, 
            satuan=satuan, 
            event=event, 
            personil=personil
        )
        db.session.add(new_bko)
        db.session.commit()
        flash('Data BKO berhasil ditambahkan!', 'success')

    lokasi_id = request.args.get('filter_lokasi_id')
    query = BKO.query

    if lokasi_id:
        query = query.filter_by(lokasi_id=lokasi_id)

    page = request.args.get('page', 1, type=int)
    per_page = 10
    bko_data_paginated = query.paginate(page=page, per_page=per_page)

    lokasi_data = Lokasi.query.all()

    return render_template('input_data_bko.html', bko_data_paginated=bko_data_paginated, lokasi_data=lokasi_data)

@bko_bp.route('/update_bko', methods=['POST'])
def update_bko():
    data = request.get_json()
    bko_entry = BKO.query.get(data['id'])
    if bko_entry:
        try:
            lokasi_id = int(data['lokasi_id'])
            jumlah_personil = int(data['jumlah_personil'])
            harga_satuan = float(data['harga_satuan'])
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid data format'})

        bko_entry.lokasi_id = lokasi_id
        bko_entry.shift = data['shift']
        bko_entry.jumlah_personil = jumlah_personil
        bko_entry.harga_satuan = harga_satuan
        bko_entry.satuan = data['satuan']
        bko_entry.event = data['event']
        bko_entry.personil = data['personil']
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Entry not found'})

@bko_bp.route('/delete_bko/<int:id>', methods=['POST'])
def delete_bko(id):
    bko_entry = BKO.query.get_or_404(id)
    db.session.delete(bko_entry)
    db.session.commit()
    flash('Data BKO berhasil dihapus!', 'success')
    return redirect(url_for('bko.bko'))

@bko_bp.route('/download_bko', methods=['GET'])
def download_bko():
    bko_data = BKO.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Lokasi', 'Shift', 'Jumlah Personil', 'Harga Satuan', 'Satuan', 'Event', 'Personil'])
    
    for bko in bko_data:
        writer.writerow([bko.lokasi.nama_lokasi, bko.shift, bko.jumlah_personil, bko.harga_satuan, bko.satuan, bko.event, bko.personil])
    
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=bko_data.csv"})
