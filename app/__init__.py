import json

from flask import Flask, render_template

from app.extensions import db

# Read username and password from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

    db_username = config['db_username']
    db_password = config['db_password']

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_username}:{db_password}@jacita-itam-jacita.a.aivencloud.com:23758/device-inventory?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extensions
    db.init_app(app)

    # ==========
    # Blueprints
    # ==========
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix = '/api')

    # ==============================
    # Error handlers
    # ==============================
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('handlers/404.html', title = '404'), 404

    return app