from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from functools import wraps

from app.controllers.auth_controller import AuthController
from app.controllers.product_controller import ProductController
from app.controllers.supplier_controller import SupplierController
from app.models import Product, Supplier, User
from app.extensions import db

web_bp = Blueprint('web', __name__)

# --- Decoradores de autenticación y autorización ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'error')
                return redirect(url_for('web.login'))
            
            # Recuperar el usuario de la DB para obtener el rol actualizado
            user = User.query.get(session['user_id'])
            if not user or user.role not in roles:
                flash('No tienes permiso para acceder a esta página.', 'error')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# --- Rutas de autenticación ---
@web_bp.route('/')
@login_required
def index():
    return redirect(url_for('web.dashboard'))

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        result = AuthController.register_user(username, email, password)
        
        if result['success']:
            # Si es el primer usuario en la DB, hacerlo admin
            if User.query.count() == 1:
                new_user = User.query.filter_by(username=username).first()
                if new_user:
                    new_user.role = 'admin'
                    db.session.commit()
                    flash('Usuario registrado exitosamente como ADMIN (primer usuario).', 'success')
            else:
                flash(result['message'], 'success')
            return redirect(url_for('web.login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('register.html')

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        result = AuthController.login_user(username, password)
        
        if result['success']:
            session['user_id'] = result['user']['id']
            session['username'] = result['user']['username']
            session['user_role'] = result['user']['role']
            flash(result['message'], 'success')
            return redirect(url_for('web.dashboard'))
        else:
            flash(result['message'], 'error')
    
    return render_template('login.html')

@web_bp.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')
    user_role = session.get('user_role')
    return render_template('dashboard.html', username=username, user_role=user_role)

@web_bp.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_role', None)
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('web.login'))


# --- Rutas CRUD de Usuarios ---
@web_bp.route('/users')
@login_required
@role_required(['admin'])
def list_users():
    result = AuthController.get_all_users()
    users = result['users'] if result['success'] else []
    return render_template('users.html', users=users)

@web_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Verificar permisos: solo admin puede editar cualquier usuario
    # o el usuario puede editar su propio perfil
    if session.get('user_role') != 'admin' and user_id != session['user_id']:
        flash('No tienes permiso para editar este usuario.', 'error')
        return redirect(url_for('web.dashboard'))

    user_data = AuthController.get_user_by_id(user_id)
    if not user_data['success']:
        flash(user_data['message'], 'error')
        return redirect(url_for('web.list_users'))

    user = user_data['user']

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') if session.get('user_role') == 'admin' else user['role']
        
        update_data = {'username': username, 'email': email, 'role': role}
        if password:
            update_data['password'] = password

        result = AuthController.update_user(user_id, **update_data)
        if result['success']:
            flash('Usuario actualizado exitosamente.', 'success')
            # Actualizar sesión si se edita el propio usuario
            if user_id == session['user_id']:
                session['username'] = username
                session['user_role'] = role
            return redirect(url_for('web.dashboard'))
        else:
            flash(result['message'], 'error')
    
    return render_template('edit_user.html', user=user, current_user_role=session.get('user_role'))

@web_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_user(user_id):
    # Impedir que un admin se auto-elimine
    if user_id == session['user_id']:
        flash('No puedes eliminar tu propia cuenta de admin.', 'error')
        return redirect(url_for('web.list_users'))

    result = AuthController.delete_user(user_id)
    if result['success']:
        flash('Usuario eliminado exitosamente.', 'success')
    else:
        flash(result['message'], 'error')
    return redirect(url_for('web.list_users'))


# --- RUTAS DE ADMINISTRACIÓN PARA E-COMMERCE ---

@web_bp.route('/admin')
@login_required
@role_required(['admin', 'subadmin'])
def admin_dashboard():
    # Información general del sistema
    total_products = Product.query.count()
    total_suppliers = Supplier.query.count()
    total_users = User.query.count()
    simulated_sales = 12345.67

    return render_template('admin/dashboard.html',
                           total_products=total_products,
                           total_suppliers=total_suppliers,
                           total_users=total_users,
                           simulated_sales=simulated_sales,
                           user_role=session.get('user_role'))


# --- CRUD de Productos ---
@web_bp.route('/admin/products')
@login_required
@role_required(['admin', 'subadmin'])
def admin_products_list():
    result = ProductController.get_all_products()
    products = result['products'] if result['success'] else []
    return render_template('admin/products/list.html', products=products, user_role=session.get('user_role'))

@web_bp.route('/admin/products/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def admin_products_create():
    suppliers = Supplier.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        supplier_id = request.form.get('supplier_id')
        supplier_id = int(supplier_id) if supplier_id else None

        result = ProductController.create_product(name, description, price, stock, supplier_id)
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('web.admin_products_list'))
        else:
            flash(result['message'], 'error')
    
    return render_template('admin/products/create_edit.html', form_title="Crear Producto", suppliers=suppliers)

@web_bp.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'subadmin'])
def admin_products_edit(product_id):
    product_data = ProductController.get_product_by_id(product_id)
    if not product_data['success']:
        flash(product_data['message'], 'error')
        return redirect(url_for('web.admin_products_list'))
    
    product = product_data['product']
    suppliers = Supplier.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        supplier_id = request.form.get('supplier_id')
        supplier_id = int(supplier_id) if supplier_id else ''

        result = ProductController.update_product(product_id, name, description, price, stock, supplier_id)
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('web.admin_products_list'))
        else:
            flash(result['message'], 'error')
    
    return render_template('admin/products/create_edit.html', form_title="Editar Producto", product=product, suppliers=suppliers)

@web_bp.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def admin_products_delete(product_id):
    result = ProductController.delete_product(product_id)
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    return redirect(url_for('web.admin_products_list'))


# --- CRUD de Proveedores ---
@web_bp.route('/admin/suppliers')
@login_required
@role_required(['admin'])
def admin_suppliers_list():
    result = SupplierController.get_all_suppliers()
    suppliers = result['suppliers'] if result['success'] else []
    return render_template('admin/suppliers/list.html', suppliers=suppliers, user_role=session.get('user_role'))

@web_bp.route('/admin/suppliers/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def admin_suppliers_create():
    if request.method == 'POST':
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        phone = request.form.get('phone')
        email = request.form.get('email')

        result = SupplierController.create_supplier(name, contact_person, phone, email)
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('web.admin_suppliers_list'))
        else:
            flash(result['message'], 'error')
    
    return render_template('admin/suppliers/create_edit.html', form_title="Crear Proveedor")

@web_bp.route('/admin/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def admin_suppliers_edit(supplier_id):
    supplier_data = SupplierController.get_supplier_by_id(supplier_id)
    if not supplier_data['success']:
        flash(supplier_data['message'], 'error')
        return redirect(url_for('web.admin_suppliers_list'))
    
    supplier = supplier_data['supplier']

    if request.method == 'POST':
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        phone = request.form.get('phone')
        email = request.form.get('email')

        result = SupplierController.update_supplier(supplier_id, name, contact_person, phone, email)
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('web.admin_suppliers_list'))
        else:
            flash(result['message'], 'error')
    
    return render_template('admin/suppliers/create_edit.html', form_title="Editar Proveedor", supplier=supplier)

@web_bp.route('/admin/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def admin_suppliers_delete(supplier_id):
    result = SupplierController.delete_supplier(supplier_id)
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    return redirect(url_for('web.admin_suppliers_list'))


# --- Ruta para información general del sistema ---
@web_bp.route('/admin/system_info')
@login_required
@role_required(['admin'])
def admin_system_info():
    total_products = Product.query.count()
    total_suppliers = Supplier.query.count()
    total_users = User.query.count()
    simulated_sales = 12345.67
    
    return render_template('admin/system_info.html',
                           total_products=total_products,
                           total_suppliers=total_suppliers,
                           total_users=total_users,
                           simulated_sales=simulated_sales)