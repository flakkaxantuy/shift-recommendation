from flask import Blueprint, render_template, request
from models import db
from models.shift_model import Schedule
from models.lokasi_model import Lokasi
from services.buat_shift_service import main, get_unique_days
from datetime import datetime, timedelta
from sqlalchemy import func
import pandas as pd

shift_bp = Blueprint('shift', __name__)

pola_shift = {
    "TAMBAK LANGON 11": ["P", "P", "M", "M", "OFF"],
    "TAMBAK LANGON 5": ["P", "P", "M", "M", "OFF"],
    "DEPO YONIF": ["P", "P", "M", "M", "OFF"],
    "PKS 7": ["P", "P", "M", "M", "OFF"],
    "DEPO JAPFA": ["P", "P", "M", "M", "OFF"],
    "TELUK BAYUR": ["P", "P", "M", "M", "OFF"],
    "DEPO 4": ["P", "P", "M", "M", "OFF"],
    "TPIL IX": ["P", "P", "M", "M", "OFF"],
    "MEDAN": ["P", "P", "M", "M", "OFF"],
    "BATULICIN": ["P", "P", "M", "M", "OFF"],
    "PERAK BARAT": ["P", "P", "M", "M", "OFF"],
    "PONTIANAK": ["P", "P", "M", "M", "OFF", "OFF"],
    "DEPO JAPFA PB": ["P", "P", "M", "M", "OFF"],
    "DEPO TB 4": ["P", "P", "M", "M", "OFF"], 
    "DEPO TL 11": ["P", "P", "M", "M", "OFF"],
    "DEPO TARAKAN": ["P", "P", "M", "M", "OFF"],
    "DEPO BALIKPAPAN": ["P", "P", "M", "M", "OFF"],
    "DEPO TRISAKTI": ["P", "P", "M", "M", "OFF"],
    "DEPO LINKAR": ["P", "P", "M", "M", "OFF", "OFF", "P"],
    "DEPO PALARAN": ["P", "P", "M", "M", "OFF"],
    "BKA KALIANAK": ["P", "P", "M", "M", "OFF"]
}

def loop_pattern(start_index, pattern, times):
    result = []
    pattern_length = len(pattern)
    
    if pattern_length != 0:
        for i in range(times+1):
            current_index = (start_index + i) % pattern_length
            result.append(pattern[current_index])
    else:
        return None
    
    return result
    
# Function to find the last occurrence of the pattern in shifts
def find_last_pattern_index(shifts, pola_shift, location):
    start_pattern_index = 0
    pattern_count = 0
    if location in pola_shift:
        pattern = pola_shift[location]
        pattern_length = len(pattern)
        for i in range(len(shifts) - len(pattern) + 1):
            if shifts[i:i + len(pattern)] == pattern:
                if start_pattern_index == 0:
                    start_pattern_index = i
                pattern_count += 1

        last_pattern_index = pattern_count * pattern_length
        indices_left = len(shifts) - last_pattern_index - start_pattern_index
        return indices_left, pattern
    
    return None

day_abbr = {
    "Monday": "SN",
    "Tuesday": "SL",
    "Wednesday": "RB",
    "Thursday": "KM",
    "Friday": "JM",
    "Saturday": "SB",
    "Sunday": "MG"
}

def get_indonesian_day_abbr(date):
    day_of_week = date.strftime("%A")
    return day_abbr.get(day_of_week)
    
@shift_bp.route('/shift', methods=['GET', 'POST'])
def shift():
    all_locations = db.session.query(Lokasi.id, Lokasi.nama_lokasi).all()

    if request.method == 'POST':
        location_id = int(request.form['location'])
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        events = ''
        first_date_bko = None
        last_date_bko = None

        # Call the main function from the service
        shifts, rabs, bko_recommendations_dict, holidays, bko_recommendations_df = main(location_id, start_date, end_date)
        hari_list = get_unique_days()

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

        date_range = [start_date_obj + timedelta(days=x) for x in range((end_date_obj - start_date_obj).days + 1)]

        # Fetch existing schedules for the location within the specified date range
        existing_schedules = db.session.query(Schedule).filter(
            Schedule.lokasi_id == location_id,
            Schedule.tanggal >= start_date_obj,
            Schedule.tanggal <= end_date_obj
        ).order_by(Schedule.tanggal).all()

        # Fetch location details based on location_id
        lokasi = Lokasi.query.filter(Lokasi.id == location_id).first()
        nama_lokasi = lokasi.nama_lokasi
        kota = lokasi.kota

        error_date_range_msg = False
        error_date_msg = False

        if len(date_range) > 31:
            error_date_range_msg = True
            return render_template('buat_shift.html', error_date_range_msg=error_date_range_msg, error_date_msg=error_date_msg, all_locations=all_locations)
        if start_date > end_date:
            error_date_msg = True
            return render_template('buat_shift.html', error_date_range_msg=error_date_range_msg, error_date_msg=error_date_msg, all_locations=all_locations)

        # Unique event bko
        if len(bko_recommendations_df) != 0:
            unique_events = bko_recommendations_df['Event'].unique()
            events = ', '.join(unique_events)

            # Sum of shift
            sum_shift = bko_recommendations_df['Shift'].sum()
            sum_jumlah_personil = bko_recommendations_df['Jumlah Personil'].sum()
            sum_total_biaya = bko_recommendations_df['Total Biaya'].sum()
            idr_format_sum_total_biaya = f'Rp {sum_total_biaya:,.0f}'.replace(',', '.')

            first_date_bko = bko_recommendations_df['Tanggal'].iloc[0]
            last_date_bko = bko_recommendations_df['Tanggal'].iloc[-1]

        lokasi_nama = Lokasi.query.filter(Lokasi.id == location_id).first().nama_lokasi

        # Organize existing schedules by employee name and shift pattern
        existing_schedules_by_name = {}
        for schedule in existing_schedules:
            if schedule.nama not in existing_schedules_by_name:
                existing_schedules_by_name[schedule.nama] = {
                    'shift_pattern': [schedule.shift],
                    'jabatan': schedule.jabatan
                }
            else:
                existing_schedules_by_name[schedule.nama]['shift_pattern'].append(schedule.shift)

        db_last_date = db.session.query(func.max(Schedule.tanggal)).filter(Schedule.lokasi_id == location_id).scalar()

        if db_last_date < end_date_obj:

            previous_schedules = db.session.query(Schedule).filter(
                Schedule.lokasi_id == location_id
            ).order_by(Schedule.tanggal.asc()).all()
                
            for schedule in previous_schedules:
                if schedule.nama not in existing_schedules_by_name:
                    existing_schedules_by_name[schedule.nama] = {
                        'shift_pattern': [schedule.shift],
                        'jabatan': schedule.jabatan
                    }
                else:
                    existing_schedules_by_name[schedule.nama]['shift_pattern'].append(schedule.shift)

            db_last_date = db.session.query(func.max(Schedule.tanggal)).filter(Schedule.lokasi_id == location_id).scalar()

            date_difference = (datetime.strptime(end_date, "%Y-%m-%d").date() - db_last_date).days

            date_range = pd.date_range(start=db_last_date + timedelta(days=1), periods=date_difference + 1, freq='D')

            for schedule.nama in existing_schedules_by_name:
                end_index, pattern = find_last_pattern_index(existing_schedules_by_name[schedule.nama]['shift_pattern'], pola_shift, lokasi_nama)

                new_shift = loop_pattern(end_index, pattern, date_difference)

                if new_shift:
                    for i in range(len(date_range)):
                        new_schedule = Schedule(
                                        nama=schedule.nama,
                                        jabatan=schedule.jabatan,
                                        lokasi_id=location_id,
                                        tanggal=date_range[i],
                                        shift=new_shift[i]
                                    )
                        db.session.add(new_schedule)

        # Retrieve updated schedules from database
        updated_schedules = db.session.query(Schedule).filter(
            Schedule.lokasi_id == location_id,
            Schedule.tanggal >= start_date_obj,
            Schedule.tanggal <= end_date_obj
        ).order_by(Schedule.tanggal).all()


        schedules_list = [
            {
                'nama': schedule.nama,
                'jabatan': schedule.jabatan,
                'lokasi_nama': nama_lokasi,
                'tanggal': schedule.tanggal.strftime('%Y-%m-%d'),
                'shift': schedule.shift
            }
            for schedule in updated_schedules
        ]

        date_difference_schedule = (end_date_obj - start_date_obj).days
        date_range_schedule = pd.date_range(start=start_date, periods=date_difference_schedule + 1, freq='D')

        days_abbr = [get_indonesian_day_abbr(date) for date in date_range_schedule]

        # Merge days_abbr and date_range_schedule into date_range_reformat
        date_range_reformat = []

        for i in range(len(date_range_schedule)):
            formatted_date = days_abbr[i] + ' ' + date_range_schedule[i].strftime('%d')
            date_range_reformat.append(formatted_date)

        return render_template(
            'buat_shift.html',
            all_locations=all_locations,
            sum_shift=sum_shift,
            days_abbr=date_range_reformat,
            error_date_range_msg=error_date_range_msg,
            error_date_msg=error_date_msg,
            sum_jumlah_personil=sum_jumlah_personil,
            sum_total_biaya=sum_total_biaya,
            idr_format_sum_total_biaya=idr_format_sum_total_biaya,
            year=start_date_obj.year,
            selected_lokasi=nama_lokasi,
            kota=kota,
            shifts=shifts,
            events=events,
            rabs=rabs,
            bko_recommendations=bko_recommendations_dict,
            print_bko_recommendations=bko_recommendations_df,
            holidays=holidays,
            hari_list=hari_list,
            date_range=date_range_schedule,
            start_date=first_date_bko,
            end_date=last_date_bko,
            schedules=schedules_list,
            start_date_not_formatted=start_date,
            end_date_not_formatted=end_date,
        )

    elif request.method == 'GET':
        return render_template('buat_shift.html', all_locations=all_locations)


