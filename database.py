import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="ironman2412",
            database="dulieusv"
        )
    except Error as e:
        print(f"Lỗi kết nối MySQL: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    connection = get_db_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        connection.commit()
        return True
    except Error as e:
        print(f"Lỗi thực thi truy vấn: {e}")
        return None
    finally:
        cursor.close()
        connection.close()