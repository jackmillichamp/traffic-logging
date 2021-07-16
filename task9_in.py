# -*- coding: utf-8 -*-

import sqlite3
import csv
import datetime
import sys
import numpy as np

# Offline summary function...
def update_logins(filename):
    with open(filename, 'r') as f:
        login_set = set(['login','logout'])
        for row in csv.reader(f):
            conn = sqlite3.connect('task9_database.db')
            c = conn.cursor()
            # Enabling foreign keys...
            c.execute("PRAGMA foreign_keys = ON")
            try:
                time = datetime.datetime.strptime(row[1], '%Y%m%d%H%M')
            except:
                print('Invalid datetime:', row[1],'\nin entry:', row)
                print('Please use yymmddhhmm format.')
            
            # Finding userid...
            query = "SELECT * FROM users WHERE username=?"
            userid = c.execute(query, (row[0],)).fetchall()[0][0]
            if row[2] not in login_set:
                print('Incorrect operation specified for row:\n', row)
                print('Please specify either login or logout. \nOther rows have still been processed.')
                continue
            if row[2] == 'login':
                # Assigning unique magic...
                while True:
                    magic = int(np.random.randint(10000000))
                    magic_chk = c.execute("SELECT * FROM sessions \
                                           WHERE magic=?", (magic,)).fetchall()
                    # Checking magic is unique...
                    if len(magic_chk) == 0:
                        break
                
                # Add login entry to table...
                query = "INSERT INTO sessions (magic, userid, start) VALUES (?,?,?)"
                c.execute(query, (magic, userid, time))
            else:
                # Add logout time to entry in table...
                query = "UPDATE sessions SET end=?, active = 0 \
                        WHERE active=1 AND userid=?"
                c.execute(query, (time, userid))
            conn.commit()
            conn.close()
        print('Logins successfully updated.')
try:
    file = sys.argv[1]
    update_logins(file)
except IndexError:
    print('Please input a csv filename (after the task9_in.py filename in cmd line)')