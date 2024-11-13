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

# GETTERS

@bp.route('/radius/get_profile', methods = ['POST'])
def api_radius_get_profile():
    username = request.form['username']

    try:
        if radius.check_user(username):
            return { 'status': 'success', 'message': 'Profile retrieved successfully.', 'profile': radius.get_profile(username) }
        
        return { 'status': 'error', 'message': 'User not found.' }
    except:
        return { 'status': 'error', 'message': 'An error occurred while retrieving the profile.' }
    
@bp.route('/radius/check_simultaneous_use_count/<string:username>', methods = ['GET'])
def api_radius_check_simultaneous_use(username):
    if not radius.check_local_entry(username):
        return { 'status': 'error', 'message': 'Local entry not found. If you are a new staff member, please contact the IT department or your division lead.' }
    
    count = radius.check_simultaneous_use_count(username)
    max = radius.get_simultaneous_use_max(username)
    
    if count >= max:
        return { 'status': 'error', 'message': f'You have used {count} out of {max} of your device quota. Please log out on other device(s).', 'count': count, 'max': max }
    else:
        return { 'status': 'success' }

# MANIPULATORS

@bp.route('/radius/change_username', methods = ['POST'])
def api_radius_change_username():
    username_old = request.form['username_old']
    username_new = request.form['username_new']
    password = request.form['password']

    if not radius.check_user(username_old):
        return { 'status': 'error', 'message': 'User not found.' }
    
    if not radius.get_password(username_old) == password:
        return { 'status': 'error', 'message': 'Authentication failed.' }
    
    if radius.check_user(username_new):
        return { 'status': 'error', 'message': 'New username is already in use.' }
    
    radius.change_username(username_old, username_new)
    return { 'status': 'success', 'message': 'Username changed successfully.' }    
    

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

@bp.route('/radius/update_profile', methods = ['POST'])
def api_radius_update_profile():
    username = request.form['username']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    workphone = request.form['workphone']
    password = request.form['password']

    print(request.form)

    try:
        if not radius.check_user(username):
            return { 'status': 'error', 'message': 'User not found.' }
        
        if not password == radius.get_password(username):
            return { 'status': 'error', 'message': 'Authentication failed.' }
        
        radius.update_profile(username, firstname, lastname, email, workphone)
        return { 'status': 'success', 'message': 'Profile updated successfully.' }
    except Exception as e:
        print(f"RADDB ERROR: {e}")
        return { 'status': 'error', 'message': 'An error occurred while updating the profile.' }
    