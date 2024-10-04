from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from models import db
import pickle
from models.lokasi_model import Lokasi 

rab_bp = Blueprint('rab', __name__)

locations = [
    "Kantor Cumi", "Kantor Enggano", "Depo Marunda", "SPIL Perak Barat",
    "BC Surabaya Raya", "Kantor PB", "Kantor Karet", "Depo Japfa",
    "Depo PKS", "Bayur", "MT Pantai Lamong", "MT Global", "PT Global"
]

days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
months = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

def format_date_indonesian(date):
    day_name = days[date.weekday()]
    month_name = months[date.month - 1]
    return f"{day_name}, {date.day} {month_name} {date.year}"

# Load the trained linear regression model
model = pickle.load(open('model/predict/demo.pkl', 'rb'))

@rab_bp.route('/rab', methods=['GET', 'POST'])
def rab():
    all_locations = db.session.query(Lokasi.id, Lokasi.nama_lokasi).all()
    bko_recommendations_dict = []
    events = ""
    sum_shift = 0
    sum_jumlah_personil = 0
    idr_format_sum_total_biaya = ""

    if request.method == 'POST':
        event_name = request.form['event']
        start_time = request.form['start-time']
        end_time = request.form['end-time']
        massa = int(request.form['massa'])
        location = int(request.form['location'])

        # predict jumlah personil bko based on massa
        bko_per_day = model.predict([[massa]])[0]
        bko_per_day = round(bko_per_day)
        
        # reformat the date
        start_date = datetime.strptime(start_time, '%Y-%m-%d')
        end_date = datetime.strptime(end_time, '%Y-%m-%d')

        # nama lokasi   
        selected_location = Lokasi.query.filter(Lokasi.id == location).first().nama_lokasi
        
        current_date = start_date
        count_event = 1
        while current_date <= end_date:
            bko_recommendations_dict.append({
                'Nomor': count_event,
                'Tanggal': format_date_indonesian(current_date),
                'Event': event_name,
                'Lokasi': selected_location,
                'Massa': massa,
                'Shift': 1,
                'Jumlah Personil': bko_per_day,
                'Harga Satuan': 260000,
                'IDR Format Biaya / Satuan':  f'Rp {260000:,}', 
                'Satuan': 'Orang/Shift',
                'Total Biaya': 260000 * bko_per_day,
                'IDR Format Total Biaya':  f'Rp {260000 * bko_per_day:,}', 
                'Personil': "TNI"
            })
            current_date += timedelta(days=1)
            count_event += 1

        # sum of jumlah personil and total biaya
        sum_shift = sum(item['Shift'] for item in bko_recommendations_dict)
        sum_jumlah_personil = sum(item['Jumlah Personil'] for item in bko_recommendations_dict)
        sum_total_biaya = sum(item['Total Biaya'] for item in bko_recommendations_dict)
        idr_format_sum_total_biaya = f'Rp {sum_total_biaya:,.0f}'.replace(',', '.')

        # get the unique events
        unique_events = list(set([item['Event'] for item in bko_recommendations_dict]))
        events = ', '.join(unique_events)

        return render_template('rab_manual.html', events=events, year=start_date.year, start_date=start_date.strftime('%d-%m-%Y'), end_date=end_date.strftime('%d-%m-%Y'), selected_location=selected_location, bko_recommendations_dict=bko_recommendations_dict, all_locations=all_locations, sum_shift=sum_shift, sum_jumlah_personil=sum_jumlah_personil, idr_format_sum_total_biaya=idr_format_sum_total_biaya)

    return render_template('rab_manual.html', all_locations=all_locations)