from flask import request, render_template
from datetime import datetime, timedelta

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

def rab():
    events = []

    if request.method == 'POST':
        event_name = request.form['event']
        start_time = request.form['start-time']
        end_time = request.form['end-time']
        bko_per_day = int(request.form['bko'])
        massa = int(request.form['massa'])
        location = request.form['location']
        
        start_date = datetime.strptime(start_time, '%Y-%m-%d')
        end_date = datetime.strptime(end_time, '%Y-%m-%d')
        
        current_date = start_date
        count_event = 1
        while current_date <= end_date:
            events.append({
                'Nomor': count_event,
                'Tanggal': format_date_indonesian(current_date),
                'Event': event_name,
                'Lokasi': location,
                'Massa': massa,
                'Shift': 1,
                'Jumlah Personil': bko_per_day,
                'Harga Satuan': 'Rp 260.000',
                'Satuan': 'Orang/Shift',
                'Total': f'Rp {260000 * bko_per_day:,}'
            })
            current_date += timedelta(days=1)
            count_event += 1

    return render_template('rab_manual.html', events=events, locations=locations)