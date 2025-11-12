from flask import Blueprint, request, jsonify
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400
    
    result = AuthController.register_user(username, email, password)
    return jsonify(result), 201 if result['success'] else 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400
    
    result = AuthController.login_user(username, password)
    return jsonify(result), 200 if result['success'] else 401

@auth_bp.route('/users', methods=['GET'])
def get_users():
    result = AuthController.get_all_users()
    return jsonify(result), 200

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    result = AuthController.get_user_by_id(user_id)
    return jsonify(result), 200 if result['success'] else 404

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    result = AuthController.update_user(user_id, username, email, password)
    return jsonify(result), 200 if result['success'] else 404

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = AuthController.delete_user(user_id)
    return jsonify(result), 200 if result['success'] else 404