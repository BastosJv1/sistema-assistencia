from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import pytz
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()

def format_datetime_local(dt, format='%d/%m/%Y às %H:%M'):
    if dt is None: return ""
    utc_tz = pytz.timezone('UTC')
    local_tz = pytz.timezone('America/Sao_Paulo')
    # A linha abaixo faz a conversão e armazena o resultado em 'utc_dt'
    utc_dt = utc_tz.localize(dt).astimezone(local_tz)
    # A CORREÇÃO ESTÁ AQUI: trocamos 'local_dt' por 'utc_dt'
    return utc_dt.strftime(format)

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma-chave-secreta-default-para-dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///oficina.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads/os_fotos')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.index'

    app.jinja_env.filters['localtime'] = format_datetime_local

    from .main.routes import main_bp
    from .os_manager.routes import os_manager_bp
    from .finance.routes import finance_bp
    from .portal.routes import portal_bp
    from .auth.routes import auth_bp
    from .cliente.routes import cliente_bp
    from .fornecedor.routes import fornecedor_bp
    from .aparelho.routes import aparelho_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(os_manager_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(portal_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(fornecedor_bp)
    app.register_blueprint(aparelho_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))