import mysql.connector
from mysql.connector import Error

#use local host for now
host = input()
user = input()
password = input()

connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password
)

#database cant already exist
database = input()

if connection.is_connected():
    cursor = connection.cursor()
    
    cursor.execute("CREATE DATABASE " + database)
    print("Database created successfully")

    cursor.close()
    connection.close()
    print("MySQL connection is closed")