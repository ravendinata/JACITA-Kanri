import json
import mysql.connector as db

with open('config.json') as f:
    config = json.load(f)

def get_radius_connection():
    return db.connect(
        host = config['radius_db_address'],
        user = config['radius_db_username'],
        password = config['radius_db_password'],
        database = config['radius_db_name']
    )

def change_password(username, password):
    conn = get_radius_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE radcheck SET value = %s WHERE username = %s AND attribute = "Cleartext-Password"', (password, username))
    conn.commit()
    cursor.close()
    conn.close()

def get_password(username):
    conn = get_radius_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM radcheck WHERE username = %s AND attribute = "Cleartext-Password"', (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

def check_user(username):
    conn = get_radius_connection()
    
    cursor = conn.cursor(buffered = True)

    cursor.execute('SELECT * FROM radcheck WHERE username = %s', (username,))
    radcheck_user = cursor.fetchone()

    cursor.execute('SELECT * FROM userinfo WHERE username = %s', (username,))
    userinfo_user = cursor.fetchone()

    cursor.close()
    
    conn.close()

    return True if radcheck_user and userinfo_user else False