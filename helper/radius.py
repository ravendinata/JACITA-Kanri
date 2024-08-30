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

# MANIPULATORS

def change_username(username_old, username_new):
    conn = get_radius_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE radcheck SET username = %s WHERE username = %s', (username_new, username_old))
    cursor.execute('UPDATE userinfo SET username = %s WHERE username = %s', (username_new, username_old))
    conn.commit()
    cursor.close()
    conn.close()

def change_password(username, password):
    conn = get_radius_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE radcheck SET value = %s WHERE username = %s AND attribute = "Cleartext-Password"', (password, username))
    conn.commit()
    cursor.close()
    conn.close()

def update_profile(username, first_name, last_name, email, workphone):
    conn = get_radius_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE userinfo SET firstname = %s, lastname = %s, email = %s, workphone = %s WHERE username = %s', (first_name, last_name, email, workphone, username))
    conn.commit()
    cursor.close()
    conn.close()

# GETTERS

def get_password(username):
    conn = get_radius_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM radcheck WHERE username = %s AND attribute = "Cleartext-Password"', (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

def get_profile(username):
    conn = get_radius_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT firstname, lastname, email, workphone FROM userinfo WHERE username = %s', (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    # JSONify the result
    json = {
        'firstname': result[0],
        'lastname': result[1],
        'email': result[2],
        'workphone': result[3]
    }

    return json

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