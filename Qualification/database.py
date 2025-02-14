import psycopg2
import yaml
import pandas as pd


class DataBase:
    def __init__(self, user_name="postgres", password="", db_name="postgres", host="localhost", port=5432):
        self.user_name = user_name
        self.password = password
        self.db_name = db_name
        self.host = host
        self.port = port

    def __get_connection(self):
        conn = psycopg2.connect(user=self.user_name, password=self.password, dbname=self.db_name, host=self.host,
                                port=self.port)
        return conn

    def execute_query(self, query):
        df = pd.read_sql_query(query, self.__get_connection())
        return df