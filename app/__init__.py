import json

from flask import Flask, render_template

from app.extensions import db

# Read username and password from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

    db_host = config['db_host']
    db_port = config['db_port']
    db_name = config['db_name']
    db_username = config['db_username']
    db_password = config['db_password']

def create_app():
    print("Starting Kanri Backend...")
    app = Flask(__name__)

    print("Configuring Database...")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extensions
    print("Initializing Database...")
    db.init_app(app)

    # ==========
    # Blueprints
    # ==========
    print("Registering Blueprints...")

    try:
        print("Importing Page Blueprint...")
        from app.main import bp as main_bp
        app.register_blueprint(main_bp)

        print("Importing API Blueprint...")
        from app.api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix = '/api')
    except ImportError as e:
        print(f"Error importing blueprints: {e}")
    except Exception as e:
        print(f"Unexpected error during blueprint registration: {e}")

    # ==============================
    # Error handlers
    # ==============================
    print("Setting up Error Handlers...")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('handlers/404.html', title = '404'), 404
    
    print("Backend setup complete.")

    return app