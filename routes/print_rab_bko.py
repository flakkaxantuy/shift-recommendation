from flask import request, render_template, Blueprint
import json
from datetime import datetime

print_rab_bko_bp = Blueprint('print_rab_bko', __name__)

@print_rab_bko_bp.route('/print_rab_bko', methods=['GET', 'POST'])
def print_rab():
    if request.method == 'POST':
        if 'print_rab_df' in request.form:
            json_all_predictions = request.form['print_rab_df']
            idr_format_sum_total_biaya = request.form['idr_format_sum_total_biaya']
            sum_shift = request.form['sum_shift']
            sum_jumlah_personil = request.form['sum_jumlah_personil']
            nomor_surat = request.form['nomor_surat']
            pihak_pertama_nama = request.form['pihak_pertama_nama']
            biaya_personil = int(request.form['biaya_personil'])
            pihak_pertama_jabatan = request.form['pihak_pertama_jabatan']
            pihak_kedua_nama = request.form['pihak_kedua_nama']
            pihak_kedua_jabatan = request.form['pihak_kedua_jabatan']
            pihak_ketiga_nama = request.form['pihak_ketiga_nama']
            pihak_ketiga_jabatan = request.form['pihak_ketiga_jabatan']
            perihal = request.form['perihal']
            note = request.form['note']

            parsed_all_predictions = json.loads(json_all_predictions)
            
            # Update the 'Shift' value based on your calculation
            for prediction in parsed_all_predictions:
                update_total_biaya = prediction['Jumlah Personil'] * prediction['Shift'] * biaya_personil
                prediction['Total Biaya'] = update_total_biaya
                prediction['IDR Format Total Biaya'] = f'Rp {update_total_biaya:,.0f}'.replace(',', '.')

            current_date = datetime.now().strftime("%d-%m-%Y")
            
            try:
                return render_template('print_pdf/rab_bko.html', current_date=current_date, biaya_personil=biaya_personil, sum_shift=sum_shift, sum_jumlah_personil=sum_jumlah_personil, idr_format_sum_total_biaya=idr_format_sum_total_biaya, perihal=perihal, rab=parsed_all_predictions, nomor_surat=nomor_surat, note=note, pihak_pertama_nama=pihak_pertama_nama, pihak_kedua_jabatan=pihak_kedua_jabatan, pihak_pertama_jabatan=pihak_pertama_jabatan, pihak_kedua_nama=pihak_kedua_nama, pihak_ketiga_jabatan=pihak_ketiga_jabatan, pihak_ketiga_nama=pihak_ketiga_nama)
            except Exception as e:
                return f"An error occurred: {str(e)}", 400
        else:
            return "KeyError: 'print_rab_df' not found in form data", 400

    return "This route only accepts POST requests", 405