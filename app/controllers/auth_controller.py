from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

class AuthController:

    @staticmethod
    def register_user(username, email, password):
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': 'El nombre de usuario ya existe'}
        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': 'El email ya está registrado'}
        
        # Hash de la contraseña
        hashed_password = generate_password_hash(password)
        
        # Crear nuevo usuario (por defecto con rol 'user')
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role='user'  # Por defecto
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return {'success': True, 'message': 'Usuario registrado exitosamente'}

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            return {'success': False, 'message': 'Usuario o contraseña incorrectos'}
        
        return {
            'success': True,
            'message': 'Inicio de sesión exitoso',
            'user': user.to_dict()
        }

    @staticmethod
    def get_all_users():
        users = User.query.all()
        return {'success': True, 'users': [user.to_dict() for user in users]}

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'Usuario no encontrado'}
        return {'success': True, 'user': user.to_dict()}

    @staticmethod
    def update_user(user_id, username=None, email=None, password=None, role=None):
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'Usuario no encontrado'}
        
        # Actualizar campos si se proporcionan
        if username:
            # Verificar que el username no esté en uso por otro usuario
            existing = User.query.filter(User.username == username, User.id != user_id).first()
            if existing:
                return {'success': False, 'message': 'El nombre de usuario ya existe'}
            user.username = username
            
        if email:
            # Verificar que el email no esté en uso por otro usuario
            existing = User.query.filter(User.email == email, User.id != user_id).first()
            if existing:
                return {'success': False, 'message': 'El email ya está registrado'}
            user.email = email
            
        if password:
            user.password = generate_password_hash(password)
            
        if role:
            # Validar que el rol sea válido
            if role not in ['admin', 'subadmin', 'user']:
                return {'success': False, 'message': 'Rol inválido'}
            user.role = role
        
        db.session.commit()
        return {'success': True, 'message': 'Usuario actualizado exitosamente'}

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'Usuario no encontrado'}
        
        db.session.delete(user)
        db.session.commit()
        return {'success': True, 'message': 'Usuario eliminado exitosamente'}
