from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Crear admin
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@ecommerce.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        print("✅ Usuario 'admin' creado")
    else:
        print("⚠️ Usuario 'admin' ya existe")
    
    # Crear subadmin
    if not User.query.filter_by(username='subadmin').first():
        subadmin = User(
            username='subadmin',
            email='subadmin@ecommerce.com',
            password=generate_password_hash('subadmin123'),
            role='subadmin'
        )
        db.session.add(subadmin)
        print("✅ Usuario 'subadmin' creado")
    else:
        print("⚠️ Usuario 'subadmin' ya existe")
    
    db.session.commit()
    print("\n🎉 Usuarios de administración listos")
    print("📝 Credenciales:")
    print("   Admin: admin / admin123")
    print("   Subadmin: subadmin / subadmin123")
