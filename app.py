from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db
from routes.home_routes import home_bp
from routes.shift_routes import shift_bp
from routes.bko_routes import bko_bp
from routes.rab_routes import rab_bp
from routes.print_pola_shift import print_pola_shift_bp
from routes.input_shift_routes import input_shift_bp
from routes.print_rab_bko import print_rab_bko_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    Migrate(app, db)
    
    # Register Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(shift_bp)
    app.register_blueprint(input_shift_bp)
    app.register_blueprint(print_rab_bko_bp)
    app.register_blueprint(bko_bp)
    app.register_blueprint(rab_bp)
    app.register_blueprint(print_pola_shift_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
