from flask import render_template

def dashboard():
    return render_template('base.html')

def driving_test_schedule():
    return render_template('driving_test_schedule.html')

def application_list():
    return render_template('application_list.html')

def scoring():
    return render_template('scoring.html')

def candidate_list():
    return render_template('candidate_list.html')

def active_driver():
    return render_template('active_driver.html')

def blacklist_driver():
    return render_template('blacklist_driver.html')
