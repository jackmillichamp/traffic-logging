# -*- coding: utf-8 -*-

import sqlite3
import hashlib
import numpy as np

def acs_db(dbfile, query, param=None):
    '''
    Requires the name of a sqlite3 database file and the query.
    Checks if parameter has been supplied for .execute() and if so uses it.
    Doesn't return the result of the query.

    Parameters
    ----------
    dbfile : String
        Filepath of database.
    query : String
        SQL query.
    param : String, optional
        Parameters to sub into SQL query. The default is None.

    Returns
    -------
    None.

    '''
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    # Enabling foreign keys...
    c.execute("PRAGMA foreign_keys = ON")
    if param == None:
        c.execute(query)
        conn.commit()
        conn.close()
    else:
        c.execute(query, param)
        conn.commit()
        conn.close()


def acs_db_rtn(dbfile, query, param=None):
    '''
    Requires the name of a sqlite3 database file and the query.
    Checks if parameter has been supplied for .execute() and if so uses it.
    Returns the result of the query.

    Parameters
    ----------
    dbfile : filepath
        Filepath of database.
    query : String
        SQL query.
    param : String, optional
        Parameters to sub into SQL query. The default is None.

    Returns
    -------
    rows : List
        SQL query output.

    '''
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    # Enabling foreign keys...
    c.execute("PRAGMA foreign_keys = ON")
    if param == None:
        rows = c.execute(query).fetchall()
        conn.commit()
        conn.close()
    else:
        rows = c.execute(query, param).fetchall()
        conn.commit()
        conn.close()
    return rows

# =============================================================================
# Set-up Database Tables...
# =============================================================================

def db_setup(db_name): 
    # Get rid of any existing tables...
    acs_db(db_name, "DROP TABLE IF EXISTS traffic")
    acs_db(db_name, "DROP TABLE IF EXISTS sessions")
    acs_db(db_name, "DROP TABLE IF EXISTS users")
    
    # Create tables...
    acs_db(db_name, "CREATE TABLE users (userid INTEGER PRIMARY KEY AUTOINCREMENT, \
           username TEXT, password TEXT, UNIQUE (username))")
    acs_db(db_name, "CREATE TABLE sessions (magic INTEGER PRIMARY KEY, \
           userid INT, start TIMESTAMP DEFAULT CURRENT_TIMESTAMP, end TIMESTAMP, \
           active NUMBER(1) DEFAULT (1), CONSTRAINT chk_active CHECK (active in (0,1)), \
           FOREIGN KEY (userid) REFERENCES users(userid))")
    acs_db(db_name, "CREATE TABLE traffic (trafficid INTEGER PRIMARY KEY AUTOINCREMENT, \
            location TEXT, type TEXT, occupancy INT, magic INT, \
            added TIMESTAMP DEFAULT CURRENT_TIMESTAMP, removed TIMESTAMP, \
            include NUMBER(1) DEFAULT (1), CONSTRAINT chk_incl CHECK (include in (0,1)), \
            CONSTRAINT type_cats CHECK (type="+"'car'"+" \
            OR type="+"'bus'"+" OR type="+"'bicycle'"+" OR type="+"'motorbike'"+" \
            OR type="+"'van'"+" OR type="+"'truck'"+" OR type="+"'taxi'"+" \
            OR type="+"'other'"+"), CONSTRAINT occup_range \
            CHECK (occupancy in (1,2,3,4)), \
            FOREIGN KEY (magic) REFERENCES sessions(magic))")
    # Populate users table...
    # Hashing passwords...
    passwords = ['password1', 'password2', 'password3', 'password4', 'password5', 'password6', \
                 'password7', 'password8', 'password9', 'password10']
    hex_passwords = []
    for password in passwords:    
        hash_object = hashlib.sha1(password.encode('utf-8'))
        hex_passwords.append(hash_object.hexdigest())
    acs_db(db_name, "INSERT INTO users (username, password) VALUES \
           ('test1', '"+hex_passwords[0]+"'), ('test2', '"+hex_passwords[1]+"'), \
           ('test3', '"+hex_passwords[2]+"'), ('test4', '"+hex_passwords[3]+"'), \
           ('test5', '"+hex_passwords[4]+"'), ('test6', '"+hex_passwords[5]+"'), \
           ('test7', '"+hex_passwords[6]+"'), ('test8', '"+hex_passwords[7]+"'), \
           ('test9', '"+hex_passwords[8]+"'), ('test10', '"+hex_passwords[9]+"')")

db_setup('initial_database.db')
db_setup('task8_database.db')
db_setup('task9_database.db')