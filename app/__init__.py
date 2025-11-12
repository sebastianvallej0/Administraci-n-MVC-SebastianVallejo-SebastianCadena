from flask import Flask
from app.extensions import db
# NO importar api_bp si no existe
from app.web_views import web_bp

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'tu-clave-secreta-super-segura-12345'
    
    db.init_app(app)
    
    # SOLO registrar web_bp
    app.register_blueprint(web_bp)
    # NO registrar api_bp
    
    with app.app_context():
        from app.models import User, Product, Supplier
        db.create_all()
        print("✅ Base de datos inicializada correctamente")
    
    return app