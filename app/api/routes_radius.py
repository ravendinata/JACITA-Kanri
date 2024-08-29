from flask import request

import helper.radius as radius
from app.api import bp

# =================
# Radius API Routes
# =================

@bp.route('/radius/authenticate', methods = ['POST'])
def api_radius_authenticate():
    username = request.form['username']
    password = request.form['password']

    if radius.check_user(username):
        if radius.get_password(username) == password:
            return { 'status': 'success', 'message': 'Authentication successful.' }
        
        return { 'status': 'error', 'message': 'Authentication failed.' }
    
    return { 'status': 'error', 'message': 'User not found.' }

@bp.route('/radius/change_username', methods = ['POST'])
def api_radius_change_username():
    username_old = request.form['username_old']
    username_new = request.form['username_new']
    password = request.form['password']

    if radius.check_user(username_old):
        if radius.get_password(username_old) == password:
            if radius.check_user(username_new):
                return { 'status': 'error', 'message': 'New username is already in use.' }

            radius.change_username(username_old, username_new)
            return { 'status': 'success', 'message': 'Username changed successfully.' }
        
        return { 'status': 'error', 'message': 'Authentication failed.' }
    
    return { 'status': 'error', 'message': 'User not found.' }

@bp.route('/radius/change_password', methods = ['POST'])
def api_radius_change_password():
    username = request.form['username']
    password_old = request.form['password_old']
    password_new = request.form['password_new']
    password_confirm = request.form['password_confirm']

    if radius.check_user(username):
        password_stored = radius.get_password(username)

        if password_stored != password_old:
            return { 'status': 'error', 'message': 'Old password does not match.' }
        
        if password_old == password_new:
            return { 'status': 'error', 'message': 'New password cannot be the same as the old password.' }

        if password_new != password_confirm:
            return { 'status': 'error', 'message': 'New password and confirm password do not match.' }

        radius.change_password(username, password_confirm)
        return { 'status': 'success', 'message': 'Password changed successfully.' }
    
    return { 'status': 'error', 'message': 'User not found.' }