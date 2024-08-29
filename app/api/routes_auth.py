from flask import request, url_for, redirect

from app.api import bp

# =========================
# Authentication API Routes
# =========================

@bp.route('/login', methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    print(f"Username: {username}")
    
    if username == 'admin' and password == 'admin':
        return redirect(url_for('page_home'))
    else:
        return redirect(url_for('page_about'))