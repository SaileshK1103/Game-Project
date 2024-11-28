import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()
class Database:
    def __init__(self):
        self.host = os.getenv('HOST'),
        self.user = os.getenv('DB_USER'),
        self.password = os.getenv('DB_PASSWORD'),
        self.database = os.getenv('DB_DATABASE')
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database =self.database
            )
            print("Database connection successful")
        except mysql.connector.Error as err:
            print(f"Error conecting to database: {err}")
            self.connection = None