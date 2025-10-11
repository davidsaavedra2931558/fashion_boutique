from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models1 import User, Product, Category  # Asegúrate de importar Category
from app.decorators import admin_required

bp = Blueprint('users', __name__)

def is_user_admin(user):
    """Detecta si el usuario es administrador (soporta varias implementaciones)."""
    try:
        if getattr(user, 'is_admin', False):
            return True
        if hasattr(user, 'is_administrator') and callable(getattr(user, 'is_administrator')):
            return user.is_administrator()
    except Exception:
        pass
    return False

def _build_products_list(queryset):
    """Normaliza objetos Product a dicts con keys estables que la plantilla usa."""
    products = []
    for p in queryset:
        name = getattr(p, 'nameProduct', None) or getattr(p, 'name', None) or 'Producto'
        id_ = getattr(p, 'idProduct', None) or getattr(p, 'id', None)
        description = getattr(p, 'description', None) or ''
        price = getattr(p, 'price', None) or 0
        try:
            price = float(price)
        except Exception:
            price = 0.0
        image = getattr(p, 'image', None) or getattr(p, 'image_url', None) or f"https://via.placeholder.com/300x300?text={name}"
        stock = getattr(p, 'stock', None) or 0
        status = getattr(p, 'status', None) or ''
        products.append({
            'id': id_,
            'name': name,
            'description': description,
            'price': price,
            'image_url': image,
            'stock': stock,
            'status': status
        })
    return products

# ============================
# RUTAS PARA CATEGORÍAS
# ============================

@bp.route('/api/categories', methods=['GET'])
@login_required
@admin_required
def get_categories():
    try:
        categories = Category.query.all()
        categories_data = []
        
        for cat in categories:
            # Contar productos en esta categoría
            product_count = Product.query.filter_by(category=cat.nameCategory).count()
            
            categories_data.append({
                'idCategory': cat.idCategory,
                'nameCategory': cat.nameCategory,
                'description': cat.description or '',
                'status': cat.status,
                'product_count': product_count
            })
        
        return jsonify({
            'success': True,
            'categories': categories_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/categories', methods=['POST'])
@login_required
@admin_required
def create_category():
    try:
        data = request.get_json()
        
        # Validar datos
        if not data.get('nameCategory'):
            return jsonify({'success': False, 'error': 'El nombre de la categoría es requerido'}), 400
        
        # Verificar si ya existe una categoría con ese nombre
        existing_category = Category.query.filter_by(nameCategory=data['nameCategory']).first()
        if existing_category:
            return jsonify({'success': False, 'error': 'Ya existe una categoría con ese nombre'}), 400
        
        # Crear nueva categoría
        new_category = Category(
            nameCategory=data['nameCategory'],
            description=data.get('description', ''),
            status='Activa'
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoría creada correctamente',
            'category': {
                'idCategory': new_category.idCategory,
                'nameCategory': new_category.nameCategory,
                'description': new_category.description,
                'status': new_category.status,
                'product_count': 0
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
@admin_required
def update_category(category_id):
    try:
        data = request.get_json()
        category = Category.query.get_or_404(category_id)
        
        # Verificar si el nuevo nombre ya existe en otra categoría
        if data.get('nameCategory') and data['nameCategory'] != category.nameCategory:
            existing_category = Category.query.filter_by(nameCategory=data['nameCategory']).first()
            if existing_category:
                return jsonify({'success': False, 'error': 'Ya existe una categoría con ese nombre'}), 400
        
        # Actualizar categoría
        if 'nameCategory' in data:
            category.nameCategory = data['nameCategory']
        if 'description' in data:
            category.description = data['description']
        if 'status' in data:
            category.status = data['status']
        
        db.session.commit()
        
        # Recalcular conteo de productos
        product_count = Product.query.filter_by(category=category.nameCategory).count()
        
        return jsonify({
            'success': True,
            'message': 'Categoría actualizada correctamente',
            'category': {
                'idCategory': category.idCategory,
                'nameCategory': category.nameCategory,
                'description': category.description,
                'status': category.status,
                'product_count': product_count
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/categories/<int:category_id>/status', methods=['PUT'])
@login_required
@admin_required
def toggle_category_status(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        
        # Cambiar estado
        category.status = 'Inactiva' if category.status == 'Activa' else 'Activa'
        
        db.session.commit()
        
        # Recalcular conteo de productos
        product_count = Product.query.filter_by(category=category.nameCategory).count()
        
        return jsonify({
            'success': True,
            'message': f'Categoría {category.status.lower()} correctamente',
            'category': {
                'idCategory': category.idCategory,
                'nameCategory': category.nameCategory,
                'description': category.description,
                'status': category.status,
                'product_count': product_count
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        
        # Verificar si hay productos asociados a esta categoría
        product_count = Product.query.filter_by(category=category.nameCategory).count()
        if product_count > 0:
            return jsonify({
                'success': False, 
                'error': f'No se puede eliminar la categoría porque tiene {product_count} producto(s) asociado(s)'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoría eliminada correctamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================
# RUTA PARA LA VISTA DE CATEGORÍAS
# ============================

@bp.route('/admin/categories')
@login_required
@admin_required
def manage_categories():
    """Vista de gestión de categorías"""
    return render_template('admin_categories.html',
                         username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Admin')))

# ============================
# TUS RUTAS EXISTENTES (MANTENIENDO LAS QUE YA TENÍAS)
# ============================

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal - Redirige según el rol"""
    admin_flag = is_user_admin(current_user)
    
    if admin_flag:
        # Si es admin, mostrar el dashboard de administrador
        total_users = User.query.count()
        try:
            total_admins = User.query.filter_by(is_admin=True).count()
            total_regular = User.query.filter_by(is_admin=False).count()
        except Exception:
            total_admins = 0
            total_regular = total_users

        return render_template('dashboard.html',
                               total_users=total_users,
                               total_admins=total_admins,
                               total_regular=total_regular,
                               username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Admin')))
    else:
        # Si es usuario regular, redirigir al perfil
        return redirect(url_for('users.profile'))


@bp.route('/admin/usuarios')
@login_required
@admin_required
def manage_users():
    """Gestión de usuarios - Solo admin"""
    users = User.query.all()
    return render_template('admin_users.html',
                           users=users,
                           username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Admin')))


@bp.route('/profile')
@login_required
def profile():
    """Perfil del usuario - Todos los roles"""
    # Intentamos filtrar por status='Activo' si existe ese campo,
    # si no, traemos los primeros 6 productos
    try:
        products_q = Product.query.filter_by(status='Activo').limit(6).all()
    except Exception:
        products_q = Product.query.limit(6).all()
    products = _build_products_list(products_q)

    role_label = 'Administrador' if is_user_admin(current_user) else 'Usuario'
    return render_template('users.html',
                           user=current_user,
                           username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Usuario')),
                           products=products,
                           orders_count=0,
                           points=100,
                           role_label=role_label)


@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Dashboard exclusivo para administradores"""
    total_users = User.query.count()
    # Intento detectar la columna is_admin; si falla uso 0/None
    try:
        total_admins = User.query.filter_by(is_admin=True).count()
        total_regular = User.query.filter_by(is_admin=False).count()
    except Exception:
        total_admins = 0
        total_regular = total_users

    return render_template('dashboard.html',
                           total_users=total_users,
                           total_admins=total_admins,
                           total_regular=total_regular,
                           username=getattr(current_user, 'nameUser', getattr(current_user, 'username', 'Admin')))


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editar perfil del usuario"""
    if request.method == 'POST':
        nameUser = request.form.get('nameUser')
        emailUser = request.form.get('emailUser')

        if not nameUser or not emailUser:
            flash('Por favor completa todos los campos', 'danger')
            return render_template('edit_profile.html', user=current_user)

        # Verificar si el email ya existe (intento robusto)
        try:
            existing_user = User.query.filter(User.emailUser == emailUser,
                                              User.idUser != getattr(current_user, 'idUser', getattr(current_user, 'id', None))).first()
        except Exception:
            # fallback: buscar por email y comparar ids manualmente
            existing_user = User.query.filter_by(emailUser=emailUser).first()
            if existing_user:
                existing_id = getattr(existing_user, 'idUser', getattr(existing_user, 'id', None))
                current_id = getattr(current_user, 'idUser', getattr(current_user, 'id', None))
                if existing_id == current_id:
                    existing_user = None

        if existing_user:
            flash('Este email ya está en uso por otro usuario', 'danger')
            return render_template('edit_profile.html', user=current_user)

        # Guardar cambios (uso setattr por si los nombres de campos varían)
        try:
            if hasattr(current_user, 'nameUser'):
                current_user.nameUser = nameUser
            elif hasattr(current_user, 'name'):
                current_user.name = nameUser

            if hasattr(current_user, 'emailUser'):
                current_user.emailUser = emailUser
            elif hasattr(current_user, 'email'):
                current_user.email = emailUser

            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('users.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error actualizando perfil: {e}', 'danger')
            return render_template('edit_profile.html', user=current_user)

    return render_template('edit_profile.html', user=current_user)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña (robusto contra distintas implementaciones del modelo)"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            flash('Por favor completa todos los campos', 'danger')
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash('Las contraseñas nuevas no coinciden', 'danger')
            return render_template('change_password.html')

        # Verificamos la contraseña actual:
        try:
            if hasattr(current_user, 'check_password') and callable(getattr(current_user, 'check_password')):
                ok = current_user.check_password(current_password)
            else:
                # fallback a check_password_hash sobre el campo password_hash
                ok = check_password_hash(getattr(current_user, 'password_hash', ''), current_password)
        except Exception:
            ok = False

        if not ok:
            flash('La contraseña actual es incorrecta', 'danger')
            return render_template('change_password.html')

        # Guardar nueva contraseña (intenta set_password, si no existe usa generate_password_hash)
        try:
            if hasattr(current_user, 'set_password') and callable(getattr(current_user, 'set_password')):
                current_user.set_password(new_password)
            else:
                current_user.password_hash = generate_password_hash(new_password)

            db.session.commit()
            flash('Contraseña actualizada correctamente', 'success')
            return redirect(url_for('users.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar contraseña: {e}', 'danger')
            return render_template('change_password.html')

    return render_template('change_password.html')