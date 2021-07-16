# -*- coding: utf-8 -*-

import sqlite3
import csv
import datetime
from collections import defaultdict
from dateutil.relativedelta import relativedelta
import math
import sys

# Offline summary function...
def user_hours(date):
    # Process dates...
    try:
        date = datetime.datetime.strptime(date, '%Y%m%d')
    except:
        print('Invalid date format:', date, '\nPlease use yyyymmdd format.')
        return
    day_start = date
    # End date to use for all periods...
    day_end = date + datetime.timedelta(days=1)
    print('End =', day_end)
    print('Day start =', day_start)
    week_start = day_end - datetime.timedelta(days=7)
    print('Week start =', week_start)
    month_start = day_end + relativedelta(months=-1)
    print('Month start =', month_start)
    conn = sqlite3.connect('task9_database.db')
    
    # Get sessions from database...
    c = conn.cursor()
    # Enabling foreign keys...
    c.execute("PRAGMA foreign_keys = ON")
    query = "SELECT users.username, sessions.start, sessions.end FROM users \
        INNER JOIN sessions \
        ON users.userid = sessions.userid \
        WHERE sessions.start BETWEEN ? AND ?"
    day_sessions = c.execute(query,(day_start, day_end)).fetchall()
    week_sessions = c.execute(query,(week_start, day_end)).fetchall()
    month_sessions = c.execute(query,(month_start, day_end)).fetchall()
    conn.commit()
    conn.close()
    
    # Process sessions...
    day_dict = defaultdict(list)
    week_dict = defaultdict(list)
    month_dict = defaultdict(list)
    dict_set = [day_dict, week_dict, month_dict]
    i = 0
    for sessions in [day_sessions, week_sessions, month_sessions]:
        curr_dict = dict_set[i]
        for session in sessions:
            t1 = datetime.datetime.strptime(session[1], '%Y-%m-%d %H:%M:%S')
            if session[2] == None:
                t2 = day_end
            else:    
                t2 = datetime.datetime.strptime(session[2], '%Y-%m-%d %H:%M:%S')
                if t2 > day_end:
                    t2 = day_end
            time_in = (t2 - t1).total_seconds() / (60*60)
            
            curr_dict[session[0]].append(time_in)
        users = list(curr_dict.keys())
        # Summing hours over each time period and rounding up...
        for user in users:
            curr_dict[user] = round(math.ceil(sum(curr_dict[user])*10)/10, 1)
        i+=1
    
    # Collating hours into correct form...
    rows = []
    for user, hours in month_dict.items():
        row = [user, 0, 0, hours]
        if user in week_dict:
            row[2] = week_dict[user]
            if user in day_dict:
                row[1] = day_dict[user]
        rows.append(row)
    
    # Writing hours to CSV...
    with open('task9_out.csv', 'w', newline="") as f: 
        write = csv.writer(f)
        write.writerows(rows)
    print('CSV file successfully created.')
try:
    date_input = sys.argv[1]
    user_hours(date_input)
except IndexError:
    print('Please input a date (after the task9_out.py filename in cmd line)')