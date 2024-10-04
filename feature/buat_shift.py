import datetime
import numpy as np
import pandas as pd
import psycopg2

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        dbname="paier",
        user="postgres",
        password="1",
        host="localhost",
        port="5432"
    )
    return conn

# Function to parse date
def parse_date(date_str):
    if isinstance(date_str, datetime.date):
        return date_str.strftime('%Y-%m-%d')
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
        try:
            return datetime.datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError(f"Time data '{date_str}' does not match any known format.")

# Function to get unique days from the database
def get_unique_days():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date_part('dow', Tanggal) FROM schedule")
    rows = cursor.fetchall()
    unique_days = [row[0] for row in rows]
    cursor.close()
    conn.close()
    return unique_days

hari_list = get_unique_days()

# Function to load shifts data from the database
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

# Function to load RABs data
def load_rabs(filename='rabs.csv'):
    import csv
    import os

    if not os.path.isfile(filename):
        return []

    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
    return data

# Function to train the model
def train_model():
    from sklearn.linear_model import LinearRegression

    X = np.array([[i] for i in range(1, 11)])
    y = np.array([2 * i + np.random.randn() for i in range(1, 11)])

    model = LinearRegression()
    model.fit(X, y)
    return model

# Function to filter shifts based on location, start date, and end date
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
                    formatted_date: shift['Shift']  # New key-value pair with formatted date
                }
                filtered_shifts.append(shift_info)
    return filtered_shifts

# Function to extract shifts
def extract_shifts(shift_dict):
    keys = list(shift_dict.keys())
    start_index = keys.index('Shift')
    return {key: shift_dict[key] for key in keys[start_index:]}

# Main function to handle shift creation
def main(location_id=None, start_date_str=None, end_date_str=None):
    if not location_id or not start_date_str or not end_date_str:
        return [], [], []

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    
    shifts = load_shifts()
    rabs = load_rabs()

    filtered_shifts = filter_shifts(shifts, location_id, start_date, end_date)
    
    model = train_model()
    data_to_predict = np.array([11, 12, 13]).reshape(-1, 1)
    # predictions = predict_shifts(model, data_to_predict)

    return filtered_shifts, rabs
