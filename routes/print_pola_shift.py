from flask import request, render_template, Blueprint
import json
from datetime import datetime, timedelta

print_pola_shift_bp = Blueprint('print_pola_shift', __name__)

days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# Dictionary to map days to their abbreviations in Indonesian
day_abbr = {
    "Monday": "SN",
    "Tuesday": "SL",
    "Wednesday": "RB",
    "Thursday": "KM",
    "Friday": "JM",
    "Saturday": "SB",
    "Sunday": "MG"
}

months = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

day_abbr = {
    "Monday": "SN",
    "Tuesday": "SL",
    "Wednesday": "RB",
    "Thursday": "KM",
    "Friday": "JM",
    "Saturday": "SB",
    "Sunday": "MG"
}

def format_date_indonesian(date):
    day_name = days[date.weekday()]
    month_name = months[date.month - 1]
    return f"{day_name}, {date.day} {month_name} {date.year}"

def get_indonesian_day_abbr(date):
    day_of_week = date.strftime("%A")
    return day_abbr.get(day_of_week)

@print_pola_shift_bp.route('/print_pola_shift', methods=['GET', 'POST'])
def print_pola_shift():
        if request.method == 'POST':
            pola_shift = request.form['print_pola_shift_df']
            start_date = request.form['print_start_date']
            end_date = request.form['print_end_date']
            location = request.form['print_location']
            schedule_sign_name = request.form['schedule_sign_name']
            schedule_sign_jabatan = request.form['schedule_sign_jabatan']
            kota = request.form['kota']
            note_schedule = request.form['note_schedule']

            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

            date_range = [start_date_obj + timedelta(days=x) for x in range((end_date_obj - start_date_obj).days + 1)]

            days_abbr = [get_indonesian_day_abbr(date) for date in date_range]

            current_date = datetime.now().strftime("%d-%m-%Y")

            # Get the month name in Indonesian
            month_name = months[start_date_obj.month - 1]

            current_date_obj = datetime.now()
            current_month_name = months[current_date_obj.month - 1]
            formatted_current_day_month_year = f"{current_date_obj.day} {current_month_name} {current_date_obj.year}"

            # Format the date as "Mei 2024"
            formatted_month_year = f"{month_name.upper()} {start_date_obj.year}"

            try:
                pola_shift = json.loads(pola_shift)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            
        return render_template('print_pdf/pola_shift.html', note_schedule=note_schedule, kota=kota, schedule_sign_name=schedule_sign_name, schedule_sign_jabatan=schedule_sign_jabatan, days_abbr=days_abbr, header_date=formatted_month_year, signature_date=formatted_current_day_month_year, location=location, current_date=current_date, schedules=pola_shift, date_range=date_range, end_date_not_formatted=end_date, start_date_not_formatted=start_date)
