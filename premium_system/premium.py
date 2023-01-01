import datetime
import schedule
import psycopg2
from data.database import Database


def check_premium():
    date = datetime.date
    conn = psycopg2.connect(Database.str_connection)
    print(date)




