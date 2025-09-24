from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user, logout_user
from app import db
from datetime import datetime, timedelta
import random

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.nameUser)

@dashboard_bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    try:
        # Importar modelos aquí para evitar problemas de importación circular
        from app.models import Product, Order, OrderDetail, User
        
        # Obtener estadísticas para el dashboard
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_users = User.query.count()
        
        # Calcular ingresos de hoy
        today = datetime.now().date()
        today_orders = Order.query.filter(Order.orderDate >= today).all()
        today_income = sum(float(order.totalAmount) for order in today_orders) if today_orders else 0
        
        # Obtener pedidos recientes
        recent_orders = Order.query.order_by(Order.orderDate.desc()).limit(5).all()
        
        # Obtener productos populares (más vendidos)
        popular_products = []
        try:
            popular_products = db.session.query(
                Product.nameProduct, 
                Product.category,
                db.func.sum(OrderDetail.quantity).label('total_sold')
            ).join(OrderDetail).group_by(Product.idProduct).order_by(db.desc('total_sold')).limit(3).all()
        except:
            # Si hay error, usar datos de ejemplo
            popular_products = []
        
        return jsonify({
            'total_products': total_products,
            'total_orders': total_orders,
            'total_users': total_users,
            'today_income': today_income,
            'recent_orders': [{
                'id': order.idOrder,
                'customer': order.user.nameUser if order.user else 'Cliente',
                'date': order.orderDate.strftime('%d/%m/%Y'),
                'amount': float(order.totalAmount),
                'status': order.status
            } for order in recent_orders],
            'popular_products': [{
                'name': name,
                'sales': total_sold,
                'category': category
            } for name, category, total_sold in popular_products]
        })
    except Exception as e:
        print(f"Error en dashboard stats: {e}")
        # Devolver datos de ejemplo si hay error
        return jsonify({
            'total_products': 0,
            'total_orders': 0,
            'total_users': 0,
            'today_income': 0,
            'recent_orders': [],
            'popular_products': []
        })

@dashboard_bp.route('/api/products')
@login_required
def get_products():
    try:
        from app.models import Product
        # OBTENER TODOS LOS PRODUCTOS SIN LÍMITE
        products = Product.query.all()
        return jsonify([{
            'id': product.idProduct,
            'name': product.nameProduct,
            'category': product.category,
            'price': float(product.price),
            'stock': product.stock,
            'status': product.status,
            'description': product.description or '',  # AÑADIR DESCRIPCIÓN
            'image': product.image or f'https://via.placeholder.com/250x300/f8f9fa/000?text={product.nameProduct}'  # AÑADIR IMAGEN
        } for product in products])
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
        return jsonify([])

@dashboard_bp.route('/api/products', methods=['POST'])
@login_required
def add_product():
    try:
        from app.models import Product
        data = request.get_json()
        new_product = Product(
            nameProduct=data['name'],
            category=data['category'],
            price=data['price'],
            stock=data['stock'],
            status=data['status'],
            description=data.get('description', ''),
            image=data.get('image', '')  # AÑADIR IMAGEN
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Producto agregado correctamente'})
    except Exception as e:
        print(f"Error agregando producto: {e}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    try:
        from app.models import Product
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        product.nameProduct = data['name']
        product.category = data['category']
        product.price = data['price']
        product.stock = data['stock']
        product.status = data['status']
        if 'description' in data:
            product.description = data['description']
        if 'image' in data:  # ACTUALIZAR IMAGEN
            product.image = data['image']
        
        db.session.commit()
        return jsonify({'message': 'Producto actualizado correctamente'})
    except Exception as e:
        print(f"Error actualizando producto: {e}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    try:
        from app.models import Product
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Producto eliminado correctamente'})
    except Exception as e:
        print(f"Error eliminando producto: {e}")
        return jsonify({'error': str(e)}), 500
    
# Rutas para gestión de usuarios
@dashboard_bp.route('/api/users')
@login_required
def get_users():
    try:
        from app.models import User
        users = User.query.all()
        return jsonify([{
            'id': user.idUser,
            'name': user.nameUser,
            'email': user.emailUser,
            'role': 'Administrador' if user.is_admin else 'Usuario',
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A',
            'status': 'Activo'
        } for user in users])
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    try:
        from app.models import User
        user = User.query.get_or_404(user_id)
        
        # No permitir eliminar el propio usuario
        if user.idUser == current_user.idUser:
            return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 400
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuario eliminado correctamente'})
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
        return jsonify({'error': str(e)}), 500

# Rutas para categorías
@dashboard_bp.route('/api/categories')
@login_required
def get_categories():
    try:
        from app.models import Category
        categories = Category.query.all()
        return jsonify([{
            'id': category.idCategory,
            'name': category.name,
            'description': category.description,
            'products_count': category.products_count if hasattr(category, 'products_count') else 0,
            'status': category.status
        } for category in categories])
    except Exception as e:
        print(f"Error obteniendo categorías: {e}")
        # Datos de ejemplo si hay error o la tabla no existe
        return jsonify([
            {'id': 'C001', 'name': 'Vestidos', 'description': 'Vestidos para mujer', 'products_count': 56, 'status': 'Activa'},
            {'id': 'C002', 'name': 'Pantalones', 'description': 'Pantalones de moda', 'products_count': 42, 'status': 'Activa'},
            {'id': 'C003', 'name': 'Camisas', 'description': 'Camisas elegantes', 'products_count': 38, 'status': 'Activa'}
        ])

@dashboard_bp.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    try:
        from app.models import Category
        data = request.get_json()
        
        # Generar ID automático si no se proporciona
        category_id = data.get('id', f'C{str(Category.query.count() + 1).zfill(3)}')
        
        new_category = Category(
            idCategory=category_id,
            name=data['name'],
            description=data.get('description', ''),
            status=data.get('status', 'Activa')
        )
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': 'Categoría agregada correctamente'})
    except Exception as e:
        print(f"Error agregando categoría: {e}")
        return jsonify({'error': str(e)}), 500

# Rutas para pedidos
@dashboard_bp.route('/api/orders')
@login_required
def get_orders():
    try:
        from app.models import Order, User
        orders = Order.query.all()
        return jsonify([{
            'id': order.idOrder,
            'customer': order.user.nameUser if order.user else 'Cliente',
            'date': order.orderDate.strftime('%d/%m/%Y'),
            'amount': float(order.totalAmount),
            'status': order.status,
            'items': order.items_count if hasattr(order, 'items_count') else 0
        } for order in orders])
    except Exception as e:
        print(f"Error obteniendo pedidos: {e}")
        # Datos de ejemplo
        return jsonify([
            {'id': 'ORD001', 'customer': 'María García', 'date': '15/03/2023', 'amount': 125.50, 'status': 'Completado', 'items': 2},
            {'id': 'ORD002', 'customer': 'Carlos López', 'date': '16/03/2023', 'amount': 89.99, 'status': 'Procesando', 'items': 1},
            {'id': 'ORD003', 'customer': 'Ana Martínez', 'date': '17/03/2023', 'amount': 210.75, 'status': 'Enviado', 'items': 3}
        ])

# Rutas para reportes
@dashboard_bp.route('/api/reports/sales')
@login_required
def get_sales_report():
    try:
        # Aquí iría la lógica para generar reportes de ventas
        return jsonify({
            'total_sales': 15000.75,
            'average_order': 125.50,
            'top_categories': [
                {'name': 'Vestidos', 'sales': 6500.25},
                {'name': 'Pantalones', 'sales': 4200.50},
                {'name': 'Camisas', 'sales': 4300.00}
            ],
            'sales_trend': [1200, 1900, 3000, 2500, 2800, 3200]  # Últimos 6 meses
        })
    except Exception as e:
        print(f"Error generando reporte: {e}")
        return jsonify({'error': str(e)}), 500

# Ruta para configuración
@dashboard_bp.route('/api/config')
@login_required
def get_config():
    try:
        # Aquí iría la lógica para obtener configuración
        return jsonify({
            'store_name': 'Fashion Boutique',
            'currency': 'MXN',
            'tax_rate': 0.16,
            'shipping_cost': 50.00,
            'free_shipping_min': 500.00
        })
    except Exception as e:
        print(f"Error obteniendo configuración: {e}")
        return jsonify({'error': str(e)}), 500

# Ruta para cerrar sesión
@dashboard_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))