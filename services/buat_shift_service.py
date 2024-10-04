import datetime
import numpy as np
import psycopg2
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression
from models import db
import pickle

def get_db_connection():
    conn = psycopg2.connect(
        dbname="paier",
        user="postgres",
        password="1",
        host="localhost",
        port="5432"
    )
    return conn

def parse_date(date_str):
    if isinstance(date_str, datetime.date):
        return date_str.strftime('%Y-%m-%d')
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
        try:
            return datetime.datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError(f"Time data '{date_str}' does not match any known format.")

def get_unique_days():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date_part('dow', Tanggal) FROM schedule")
    rows = cursor.fetchall()
    unique_days = [row[0] for row in rows]
    cursor.close()
    conn.close()
    return unique_days

def load_shifts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama, jabatan, lokasi_id, tanggal, shift FROM schedule")
    rows = cursor.fetchall()
    shifts = []
    for row in rows:
        shift = {
            'Nama': row[0],
            'Jabatan': row[1],
            'Lokasi_id': row[2],
            'Tanggal': parse_date(row[3].strftime('%Y-%m-%d') if isinstance(row[3], datetime.date) else row[3]),
            'Shift': row[4]
        }
        shifts.append(shift)
    cursor.close()
    conn.close()
    return shifts

def load_rabs(filename='rabs.csv'):
    import csv
    import os

    if not os.path.isfile(filename):
        return []

    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
    return data

def train_model():
    X = np.array([[i] for i in range(1, 11)])
    y = np.array([2 * i + np.random.randn() for i in range(1, 11)])

    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_shifts(model, data):
    data = np.array(data).reshape(-1, 1)
    predictions = model.predict(data)
    return predictions

def filter_shifts(shifts, location_id, start_date, end_date):
    filtered_shifts = []
    for shift in shifts:
        shift_date = datetime.datetime.strptime(shift['Tanggal'], '%Y-%m-%d').date()
        if shift['Lokasi_id'] == location_id and start_date.date() <= shift_date <= end_date.date():
            nama_exists = False
            formatted_date = shift_date.strftime("%A, %d %B %Y").replace(
                "Monday", "Senin"
            ).replace(
                "Tuesday", "Selasa"
            ).replace(
                "Wednesday", "Rabu"
            ).replace(
                "Thursday", "Kamis"
            ).replace(
                "Friday", "Jumat"
            ).replace(
                "Saturday", "Sabtu"
            ).replace(
                "Sunday", "Minggu"
            ).replace(
                "January", "Januari"
            ).replace(
                "February", "Februari"
            ).replace(
                "March", "Maret"
            ).replace(
                "April", "April"
            ).replace(
                "May", "Mei"
            ).replace(
                "June", "Juni"
            ).replace(
                "July", "Juli"
            ).replace(
                "August", "Agustus"
            ).replace(
                "September", "September"
            ).replace(
                "October", "Oktober"
            ).replace(
                "November", "November"
            ).replace(
                "December", "Desember"
            )
            for existing_shift in filtered_shifts:
                if existing_shift['Nama'] == shift['Nama']:
                    existing_shift[formatted_date] = shift['Shift']
                    nama_exists = True
                    break
            if not nama_exists:
                shift_info = {
                    'Nama': shift['Nama'],
                    'Jabatan': shift['Jabatan'],
                    'Lokasi_id': shift['Lokasi_id'],
                    'Tanggal': shift_date.strftime('%Y-%m-%d'),
                    'Shift': shift['Shift'],
                    formatted_date: shift['Shift']
                }
                filtered_shifts.append(shift_info)
    return filtered_shifts

def fetch_holidays(start_date, end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    current_date =datetime.datetime.now()

    year = current_date.year
    response = requests.get(f"https://dayoffapi.vercel.app/api?year={year}")
    holidays = response.json()

    holidays_in_range = [
        holiday for holiday in holidays
        if start_date <= pd.to_datetime(holiday['tanggal']).date() <= end_date
    ]

    return holidays_in_range

event_mapping = [
    {"keyword": "idul fitri", "event_api": "Idul Fitri"},
    {"keyword": "idul adha", "event_api": "Idul Adha"},
    {"keyword": "natal", "event_api": "Natal"},
    {"keyword": "tahun baru", "event_api": "Tahun Baru"},
    {"keyword": "kemerdekaan indonesia", "event_api": "Kemerdekaan"},
    {"keyword": "hari raya nyepi", "event_api": "Nyepi"},
    {"keyword": "hari raya imlek", "event_api": "Imlek"},
    {"keyword": "hari raya waisak", "event_api": "Waisak"},
    {"keyword": "maulid nabi muhammad", "event_api": "Maulid Nabi Muhammad SAW"}
]

def map_event_to_keywords(event):
    keywords_set = set()
    for mapping in event_mapping:
        if mapping['event_api'].lower() in event.lower():
            keywords_set.add(mapping['keyword'])
    return list(keywords_set)

# Mapping for Indonesian days and months
days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
months = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

def format_date_indonesian(date):
    day_name = days[date.weekday()]
    month_name = months[date.month - 1]
    return f"{day_name}, {date.day} {month_name} {date.year}"

# Load encoders and models
tree_jumlah_personil = pickle.load(open('model/predict/tree_jumlah_personil.pkl', 'rb'))
tree_shift = pickle.load(open('model/predict/logreg_shift.pkl', 'rb'))

label_encoder_event = pickle.load(open('model/encode/label_encoder_event.pkl', 'rb'))
label_encoder_lokasi = pickle.load(open('model/encode/label_encoder_lokasi.pkl', 'rb'))
label_encoder_personil = pickle.load(open('model/encode/label_encoder_personil.pkl', 'rb'))

def predict_shifts(data, count_event):
    predictions_list = []

    data['Lokasi'] = label_encoder_lokasi.transform(data['Lokasi'])
    data['Event'] = label_encoder_event.transform(data['Event'])

    data['Hari'] = count_event
    features = data[['Hari', 'Lokasi', 'Event']].values

    predicted_shift = tree_shift.predict(features)
    predicted_jumlah_personil = tree_jumlah_personil.predict(features)

    lokasi_decoded = label_encoder_lokasi.inverse_transform(data['Lokasi'])
    event_decoded = label_encoder_event.inverse_transform(data['Event'])

    for i in range(len(data)):
        biaya_per_satuan = 260000
        total_biaya = biaya_per_satuan * predicted_shift[i] * predicted_jumlah_personil[i]
        
        predictions_list.append({
            'Nomor': count_event,
            'Lokasi': lokasi_decoded[i],
            'Event': event_decoded[i].title(),
            'Tanggal': data['Tanggal'].iloc[i],
            'Tanggal Not Formatted': data['Tanggal Not Formatted'].iloc[i],
            'Biaya / Satuan': biaya_per_satuan,
            'Total Biaya': total_biaya,
            'IDR Format Biaya / Satuan': f'Rp {biaya_per_satuan:,.0f}'.replace(',', '.'),
            'IDR Format Total Biaya': f'Rp {total_biaya:,.0f}'.replace(',', '.'),
            'Shift': predicted_shift[i],
            'Jumlah Personil': predicted_jumlah_personil[i],
            'Personil': "TNI"
        })


    predictions_df = pd.DataFrame(predictions_list)
    return predictions_df

def main(location_id=None, start_date_str=None, end_date_str=None):
    if not location_id or not start_date_str or not end_date_str:
        return [], [], []

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    
    shifts = load_shifts()
    rabs = load_rabs()
    filtered_shifts = filter_shifts(shifts, location_id, start_date, end_date)

    holidays = fetch_holidays(start_date_str, end_date_str)
    events = [(holiday['keterangan'], holiday['tanggal']) for holiday in holidays]
    all_predictions = []

    count_event = 0
    for event, tanggal in events:
        event_bko = map_event_to_keywords(event)
        if event_bko:
            count_event += 1
            for name_event in event_bko:
                input_data = pd.DataFrame({
                    'Lokasi': ['Kantor Enggano'],
                    'Event': [name_event],
                    'Tanggal': format_date_indonesian(datetime.datetime.strptime(tanggal, "%Y-%m-%d")),
                    'Tanggal Not Formatted': tanggal,
                })

                predictions = predict_shifts(input_data, count_event)
                all_predictions.append(predictions)

    if all_predictions:
        predictions_df = pd.concat(all_predictions, ignore_index=True)
        predictions_dict = predictions_df.to_dict(orient='records')
        return filtered_shifts, rabs, predictions_dict, holidays, predictions_df

    return filtered_shifts, rabs, '', holidays, ''