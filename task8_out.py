# -*- coding: utf-8 -*-

import sqlite3
import csv
import datetime
import sys

# Offline summary function...
def off_summary(start_date, end_date):
    try:
        start = datetime.datetime.strptime(start_date, '%Y%m%d%H%M')
        end = datetime.datetime.strptime(end_date, '%Y%m%d%H%M')
    except:
        print('Invalid datetime format:', start_date,',', end_date, '\nPlease use yyyymmddhhmm format.')
        return
    if start > end:
        print('Error: Start date later than end date, CSV not created')
        return
    conn = sqlite3.connect('task8_database.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")
    query = "SELECT location, type, occupancy, COUNT(occupancy) FROM traffic WHERE include = 1 \
            AND added BETWEEN ? AND ? GROUP BY location, type, occupancy"
    rows = c.execute(query,(start, end)).fetchall()
    conn.commit()
    conn.close()
    items = []
    if len(rows) == 0:
        print('No results!')
        with open('task8_out.csv', 'w', newline=""):
            pass
        return
    init_loc = rows[0][0]
    init_type = rows[0][1]
    occs = [0,0,0,0]
    item = [init_loc, init_type]
    for i in range(len(rows)):
        row = rows[i]
        loc = row[0]
        type = row[1]
        occ_n = row[3]
        if loc == init_loc:
            if type == init_type:
                occs[row[2] - 1] = occ_n
            else:
                item += occs
                items.append(item)
                item = [loc, type]
                init_type = type
                occs = [0,0,0,0]
                occs[row[2] - 1] = occ_n
        else:
            item += occs
            items.append(item)
            item = [loc, type]
            init_loc = loc
            init_type = type
            occs = [0,0,0,0]
            occs[row[2] - 1] = occ_n
    item += occs
    items.append(item)
    # Writing to csv file named 'task8_out.csv'...
    with open('task8_out.csv', 'w', newline="") as f: 
        write = csv.writer(f)
        write.writerows(items)
    print('CSV file successfully created.')

# Querying the database...
# Please input start and end dates here, in yyyymmddhhmm format...
# example start: '201806021254'
# example end: '202012151230'
try:
    start_date = sys.argv[1]
    print()
    end_date = sys.argv[2]
    off_summary(start_date, end_date)
except IndexError:
    print('Please input start and end date and times (after the task8_out.py filename in cmd line)')