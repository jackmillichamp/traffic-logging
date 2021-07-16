# -*- coding: utf-8 -*-

import sqlite3
import csv
import datetime
import sys
import numpy as np

# Offline summary function...
def update_summary(filename):
    with open(filename, 'r') as f:
        magic = int(np.random.randint(10000000))
        conn = sqlite3.connect('task8_database.db')
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON")
        c.execute("INSERT INTO sessions (magic, userid) VALUES (?, 1)", \
                  (magic,))
        conn.commit()
        conn.close()
        types = set(['car','bus','taxi','bicycle','motorbike','van','truck','other'])
        oper_set = set(['add','undo'])
        for row in csv.reader(f):
            conn = sqlite3.connect('task8_database.db')
            c = conn.cursor()
            # Checking input has correct form...
            try:
                date = datetime.datetime.strptime(row[0], '%Y%m%d%H%M')
            except:
                print('Invalid datetime:', row[0],'\nin entry:', row)
                print('Please use yyyymmddhhmm form.')
                print('Other rows have still been processed.')
                continue
            if row[1] not in oper_set:
                print('Incorrect operation specified for row:\n', row)
                print('Please specify either add or undo. \nOther rows have still been processed.')
                continue
            elif row[3] not in types:
                print('Incorrect vehicle type for row:\n', row)
                print('Please specify either car,bus,taxi,bicycle,motorbike,van,truck,other.')
                print('Other rows have still been processed.')
                continue
            # Input has correct form, continue...
            if row[1] == 'add':
                # Add entry to table...
                query = "INSERT INTO traffic (magic, location, type, occupancy, added) VALUES (?,?,?,?,?)"
                c.execute(query, (magic, row[2], row[3], row[4], date))
            else:
                # Decativate entry in table...
                query = "UPDATE traffic SET include = 0, removed = ? \
                        WHERE trafficid IN (SELECT trafficid FROM traffic WHERE magic=? AND location=? \
                        AND type=? AND occupancy=? AND include = 1 ORDER BY added DESC LIMIT 1)"
                c.execute(query, (date, magic, row[2], row[3], row[4]))
            conn.commit()
            conn.close()
        conn = sqlite3.connect('task8_database.db')
        c = conn.cursor()
        c.execute("UPDATE sessions SET active=0, end=CURRENT_TIMESTAMP \
                  WHERE magic=? AND userid=1", (magic,))
        conn.commit()
        conn.close()
        print('Summary Updated')
try:
    file = sys.argv[1]
    update_summary(file)
except IndexError:
    print('Please input a csv filename (after the task8_in.py filename in cmd line)')