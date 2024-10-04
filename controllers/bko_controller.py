from flask import request, flash, redirect, url_for, render_template
from services.input_bko_service import insert_bko, fetch_all_bko, delete_bko, update_bko

def input_bko():
    if request.method == 'POST':
        if request.form.get('action') == 'insert':
            lokasi = request.form.get('lokasi')
            shift = request.form.get('shift')
            jumlah_personil = request.form.get('jumlah_personil')
            harga_satuan = request.form.get('harga_satuan')
            satuan = request.form.get('satuan')
            event = request.form.get('event')
            personil = request.form.get('personil')

            success = insert_bko(lokasi, shift, jumlah_personil, harga_satuan, satuan, event, personil)

            if success:
                flash('Data berhasil dimasukkan!', 'success')
            else:
                flash('Terjadi kesalahan saat memasukkan data!', 'danger')

        elif request.form.get('action') == 'update':
            bko_id = request.form.get('bko_id')
            tanggal = request.form.get('tanggal')
            lokasi = request.form.get('lokasi')
            shift = request.form.get('shift')
            jumlah_personil = request.form.get('jumlah_personil')
            harga_satuan = request.form.get('harga_satuan')
            satuan = request.form.get('satuan')
            event = request.form.get('event')
            personil = request.form.get('personil')

            success = update_bko({
                'id': bko_id,
                'tanggal': tanggal,
                'lokasi': lokasi,
                'shift': shift,
                'jumlah_personil': jumlah_personil,
                'harga_satuan': harga_satuan,
                'satuan': satuan,
                'event': event,
                'personil': personil
            })

            if success:
                flash('Data berhasil diperbarui!', 'success')
            else:
                flash('Terjadi kesalahan saat memperbarui data!', 'danger')

    bko_data = fetch_all_bko()
    return render_template('input_data_bko.html', bko_data=bko_data)

def delete_bko_route(id):
    success = delete_bko(id)
    if success:
        flash('Data berhasil dihapus!', 'success')
    else:
        flash('Terjadi kesalahan saat menghapus data!', 'danger')
    return redirect(url_for('input_bko'))
