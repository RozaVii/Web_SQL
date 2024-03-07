import sqlite3
import pandas as pd

con = sqlite3.connect("swimming_pool.db")

cursor = con.cursor()

cursor.execute("SELECT * FROM client")
print(cursor.fetchall())

cursor.execute("SELECT * FROM coach")
print(cursor.fetchall())

cursor.execute("SELECT * FROM service")
print(cursor.fetchall())

cursor.execute("SELECT * FROM schedule")
print(cursor.fetchall())

cursor.execute("SELECT * FROM schedule_date")
print(cursor.fetchall())

cursor.execute("SELECT * FROM record")
print(cursor.fetchall())

con.close()
