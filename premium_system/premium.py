from datetime import datetime, timedelta
import datetime
import calendar
import schedule
import psycopg2
import asyncpg
import discord
from data.database import Database


def check_premium():
    date = datetime.date.today()
    conn = psycopg2.connect(Database.str_connection)
    cur = conn.cursor()
    sql_get_until_date_premium_query = "SELECT * FROM premium_users;"
    cur.execute(sql_get_until_date_premium_query)
    result = cur.fetchall()
    if result:
        for record in result:
            print(type(record[2]), type(date))
            if record[2] < date:
                query_id = record[0]
                sql_on_delete_expired_premium_status_query = f"DELETE FROM premium_users WHERE id = {query_id}"
                cur.execute(sql_on_delete_expired_premium_status_query)
                conn.commit()
            print(record[1])
    else:
        print("Нету премов")
    conn.close()


async def has_premium(user: discord.User) -> bool:
    conn = await asyncpg.connect(Database.str_connection)
    has_premium_query = f"SELECT * FROM premium_users WHERE user_id = {user.id}"
    result = await conn.fetch(has_premium_query)
    if result:
        return True
    return False


async def give_premium(user: discord.User, months: int):
    conn = await asyncpg.connect(Database.str_connection)
    src_date = datetime.date.today()
    date = add_months(src_date, months)
    user_id = user.id
    sql_add_premium_query = "DO $$" \
                            "BEGIN " \
                            "IF EXISTS (" \
                                "SELECT * FROM premium_users " \
                                f"WHERE user_id = {user_id}) THEN " \
                                    f"DELETE FROM premium_users WHERE user_id = {user_id};" \
                                    f"INSERT INTO premium_users (user_id, until_date) VALUES ({user_id}, '{date.strftime('%Y%m%d')}');" \
                                f"ELSE " \
                                    f"INSERT INTO premium_users (user_id, until_date) VALUES ({user_id}, '{date.strftime('%Y%m%d')}');" \
                                f"END IF;" \
                            f"END $$;"
    await conn.fetch(sql_add_premium_query)
    await conn.close()

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)



