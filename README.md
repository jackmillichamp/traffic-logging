# Traffic logging website (SQL, Databases, Python)

• Created a website with secure user login system for road traffic logging

• Designed a secure backend relational database and incorporated secure SQL querying into website interactions via python, allowing for multiple simultaneous users and cookie sharing

• Developed multiple python scripts to summarise entered traffic data from the database over specified time periods, incorporating advanced SQL queuing

My final report can be found under "Mini Project Report.pdf". Final grade: First class (98%).

Here's a view of the traffic logging webpages:

![image](https://github.com/jackmillichamp/traffic-logging/blob/main/pages_overview.png)

## Instructions for running the server & scripts

### Running the server...
This 
Each time the server is started, the database initialiser file is run (db_initialiser.py). 
This creates a fresh intial database automatically (overwriting initial_database.db).

### Running tasks 8 and 9...
As well as creating a fresh initial_database.db for server use, the database initialiser file also creates task8_database.db and task9_database.db, 
which are used in tasks 8 & 9 respectively. If a fresh empty database is required for either task 8 or 9, please run the db_initialiser.py file from the command line: 
e.g. 'python db_initialiser.py'.
(Make sure you are in the correct directory, inside the 'code' folder - this also applies to all of the following instructions that use the command line).

### Task 8 in...
To successfully update traffic entries using a csv file, please run task8_in.py from the command line followed by the csv filename:
e.g. 'python task8_in.py traffic_observations.csv' (no quotations are neccesary around the csv filename).

### Task 8 out...
To output a csv file of all traffic entries between a given date and time range, please run task8_out.py from the command line followed by the start date and time
and the end date and time, as shown below (both datetimes must be given in yyyymmddhhmm form):
e.g. 'python  task8_out.py 202011141230 202011141545'
The output csv file will have the filename 'task8_out.csv'.

### Task 9 in...
To successfully update login entries using a csv file, please run task9_in.py from the command line followed by the csv filename:
e.g. 'python task9_in.py logins.csv' (no quotations are neccesary around the csv filename).

### Task 9 out...
To output a csv file of all login entries over the past day, week & month from a given date, please run task9_out.py from the command line followed by the date, 
as shown below (the date must be given in yyyymmdd form):
e.g. 'python  task9_out.py 20201225'
The output csv file will have the filename 'task9_out.csv'. The date ranges over which login entries are pulled are inclusive of the date entered.
