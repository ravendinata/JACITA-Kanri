import hashlib

from flask import request

from app.api import bp
from app.extensions import db
from app.models.auth import Users

# =========================
# Authentication API Routes
# =========================

@bp.route('/auth/login', methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = Users.query.filter_by(username = username).first()
    
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    password_salt = hashlib.md5(f"{password_md5}{username}".encode()).hexdigest()

    if user is None:
        return { 'status': 'error', 'message': 'Username not found.' }
    
    if user.password != password_salt:
        return { 'status': 'error', 'message': 'Login failed.' }

    return { 'status': 'success', 'message': 'Login successful.' }

@bp.route('/auth/create_user', methods = ['POST'])
def create_user():
    username = request.form['username']
    password = request.form['password']

    password_md5 = hashlib.md5(password.encode()).hexdigest()
    password_salt = hashlib.md5(f"{password_md5}{username}".encode()).hexdigest()

    user = Users(username = username, password = password_salt)
    db.session.add(user)
    db.session.commit()

    return { 'status': 'success', 'message': 'User created successfully.' }

@bp.route('/auth/change_password', methods = ['POST'])
def kanri_change_password():
    username = request.form['username']
    password_old = request.form['password_old']
    password_new = request.form['password_new']

    user = Users.query.filter_by(username = username).first()

    if user is None:
        return { 'status': 'error', 'message': 'Username not found.' }

    password_old_md5 = hashlib.md5(password_old.encode()).hexdigest()
    password_old_salt = hashlib.md5(f"{password_old_md5}{username}".encode()).hexdigest()

    if user.password != password_old_salt:
        return { 'status': 'error', 'message': 'Old password is incorrect.' }
    
    password_new_md5 = hashlib.md5(password_new.encode()).hexdigest()
    password_new_salt = hashlib.md5(f"{password_new_md5}{username}".encode()).hexdigest()
    user.password = password_new_salt
    
    db.session.commit()

    return { 'status': 'success', 'message': 'Password changed successfully.' }
    