import config
import psycopg2
from psycopg2 import pool


class Database:
    def __init__(self):
        try:   #подключение к БД
            self.conn = psycopg2.connect(database=config.db_name,
                                        user=config.user,
                                        password=config.password,
                                        host=config.host)
            self.conn.set_session(autocommit=True)  #установление автокоммита
            if (self.conn):
                print("Connection successfully")
            cursor = self.conn.cursor()
            if (cursor):
                print("successfully recived connection from connection pool ")
                table_create = """
                            CREATE TABLE IF NOT EXISTS visitors(
                            host VARCHAR(255) NOT NULL,
                            server_name VARCHAR(255) NOT NULL,
                            time TIME with time zone NOT NULL,
                            date DATE NOT NULL,
                            country_name VARCHAR(255) NOT NULL,
                            region_name VARCHAR(255) NOT NULL,
                            city_name VARCHAR(255) NOT NULL,
                            os_family VARCHAR(255) NOT NULL,
                            browser_family VARCHAR(255) NOT NULL,
                            device_family VARCHAR(255) NOT NULL,
                            other_duid VARCHAR(255) NOT NULL);
                            """
                cursor.execute(table_create)
                cursor.close()
                print("table was created")
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)

    def add_visit(self, host, server_name, time, date, country_name, region_name, city_name, os_family,
                  browser_family, device_family, other_duid):
        cursor = self.conn.cursor()
        sql = f"""INSERT INTO visitors VALUES ('{host}', '{server_name}', '{time}', '{date}', '{country_name}', '{region_name}', '{city_name}', '{os_family}',
                  '{browser_family}', '{device_family}', '{other_duid}');"""
        try:
            cursor.execute(sql)
            cursor.close()
        except Exception as e:
            print("ploho")
        print(sql)
