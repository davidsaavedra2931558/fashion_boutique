from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app import db
from app.models1 import Product
from decimal import Decimal

products_bp = Blueprint('products', __name__)

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    """Obtener todos los productos activos (API JSON)"""
    try:
        # OBTENER TODOS LOS PRODUCTOS ACTIVOS SIN LÍMITE
        products = Product.query.filter_by(status='Activo').all()
        return jsonify([{
            'id': product.idProduct,
            'name': product.nameProduct,
            'description': product.description or '',
            'price': float(product.price),
            'image_url': product.image or f'https://via.placeholder.com/250x300/f8f9fa/000?text={product.nameProduct}',
            'category': product.category,
            'stock': product.stock,
            'status': product.status,
            'details': getattr(product, 'details', '')  # Detalles adicionales si existen
        } for product in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ NUEVA RUTA: Página HTML de productos por categoría
@products_bp.route('/categoria/<category_name>')
def category_products_page(category_name):
    """Página HTML de productos por categoría"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 30
        
        # Filtrar productos por categoría (case insensitive)
        products_query = Product.query.filter(
            Product.category.ilike(f'%{category_name}%'),
            Product.status == 'Activo'
        )
        
        pagination = products_query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
        
        products = pagination.items
        
        # Convertir productos a formato para la template
        products_data = []
        for product in products:
            products_data.append({
                'id': product.idProduct,
                'name': product.nameProduct,
                'description': product.description or '',
                'price': float(product.price),
                'image_url': product.image or f'https://via.placeholder.com/300x400/f8f9fa/000?text={product.nameProduct}',
                'category': product.category,
                'stock': product.stock,
                'status': product.status
            })
        
        return render_template('category_products.html', 
                             products=products_data,
                             category_name=category_name,
                             current_page=page,
                             total_pages=pagination.pages,
                             has_next=pagination.has_next,
                             has_prev=pagination.has_prev)
                             
    except Exception as e:
        return render_template('error404.html'), 404

# ✅ RUTA: Página HTML de detalles del producto
@products_bp.route('/producto/<int:product_id>')
def product_detail(product_id):
    """Página de detalles del producto (HTML)"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Convertir producto a formato para la template
        product_data = {
            'id': product.idProduct,
            'name': product.nameProduct,
            'description': product.description or '',
            'price': float(product.price),
            'image_url': product.image or f'https://via.placeholder.com/500x600/f8f9fa/000?text={product.nameProduct}',
            'category': product.category,
            'stock': product.stock,
            'status': product.status,
            'details': getattr(product, 'details', ''),
            'size': getattr(product, 'size', 'No especificado'),
            'color': getattr(product, 'color', 'No especificado')
        }
        
        # Productos relacionados (misma categoría)
        related_products = Product.query.filter(
            Product.category == product.category,
            Product.idProduct != product_id,
            Product.status == 'Activo'
        ).limit(4).all()
        
        # Convertir productos relacionados
        related_products_data = []
        for related_product in related_products:
            related_products_data.append({
                'id': related_product.idProduct,
                'name': related_product.nameProduct,
                'price': float(related_product.price),
                'image_url': related_product.image or f'https://via.placeholder.com/250x300/f8f9fa/000?text={related_product.nameProduct}',
                'category': related_product.category
            })
        
        return render_template('product_detail.html', 
                             product=product_data, 
                             related_products=related_products_data)
    except Exception as e:
        return render_template('error404.html'), 404

@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """Obtener detalles específicos de un producto (API JSON)"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'id': product.idProduct,
            'name': product.nameProduct,
            'description': product.description or '',
            'price': float(product.price),
            'image_url': product.image or f'https://via.placeholder.com/300x300/f8f9fa/000?text={product.nameProduct}',
            'category': product.category,
            'stock': product.stock,
            'status': product.status,
            'details': getattr(product, 'details', ''),
            'size': getattr(product, 'size', 'No especificado'),
            'color': getattr(product, 'color', 'No especificado')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/api/products/category/<category_name>', methods=['GET'])
def get_products_by_category(category_name):
    """Obtener productos por categoría (API JSON)"""
    try:
        products = Product.query.filter_by(
            category=category_name, 
            status='Activo'
        ).all()
        
        return jsonify([{
            'id': product.idProduct,
            'name': product.nameProduct,
            'description': product.description or '',
            'price': float(product.price),
            'image_url': product.image or f'https://via.placeholder.com/250x300/f8f9fa/000?text={product.nameProduct}',
            'category': product.category,
            'stock': product.stock,
            'status': product.status
        } for product in products])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/api/products', methods=['POST'])
@login_required
def add_product():
    """Agregar nuevo producto"""
    try:
        # Verificar si es JSON o form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Convertir tipos de datos para form data
            if 'price' in data:
                data['price'] = float(data['price'])
            if 'stock' in data:
                data['stock'] = int(data['stock'])
        
        # Validar campos requeridos
        required_fields = ['name', 'category', 'price', 'stock']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
            }), 400
        
        # Validar tipos de datos
        try:
            price = float(data['price'])
            stock = int(data['stock'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Precio y stock deben ser valores numéricos'
            }), 400
        
        new_product = Product(
            nameProduct=data['name'],
            category=data['category'],
            price=price,
            stock=stock,
            description=data.get('description', ''),
            image=data.get('image', ''),
            status='Activo' if stock > 0 else 'Inactivo'
        )
        
        # Añadir campos adicionales si existen en el modelo
        if hasattr(Product, 'details') and 'details' in data:
            new_product.details = data['details']
        if hasattr(Product, 'size') and 'size' in data:
            new_product.size = data['size']
        if hasattr(Product, 'color') and 'color' in data:
            new_product.color = data['color']
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Producto agregado correctamente',
            'product': {
                'id': new_product.idProduct,
                'name': new_product.nameProduct
            }
        }), 201  # Código 201 para creado
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al agregar el producto: {str(e)}'
        }), 500

@products_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """Actualizar producto existente"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # Verificar si es JSON o form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Convertir tipos de datos para form data
            if 'price' in data:
                data['price'] = float(data['price'])
            if 'stock' in data:
                data['stock'] = int(data['stock'])
        
        # Validar campos
        if 'name' in data:
            product.nameProduct = data['name']
        if 'category' in data:
            product.category = data['category']
        if 'price' in data:
            try:
                product.price = float(data['price'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'El precio debe ser un valor numérico'
                }), 400
        if 'stock' in data:
            try:
                product.stock = int(data['stock'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'El stock debe ser un valor numérico'
                }), 400
        
        if 'description' in data:
            product.description = data['description']
        if 'image' in data:
            product.image = data['image']
        
        # Actualizar campos adicionales si existen
        if hasattr(product, 'details') and 'details' in data:
            product.details = data['details']
        if hasattr(product, 'size') and 'size' in data:
            product.size = data['size']
        if hasattr(product, 'color') and 'color' in data:
            product.color = data['color']
        
        # Actualizar estado basado en stock
        product.status = 'Activo' if product.stock > 0 else 'Inactivo'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Producto actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar el producto: {str(e)}'
        }), 500

@products_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """Eliminar producto"""
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Producto eliminado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar el producto: {str(e)}'
        }), 500

# ✅ NUEVA RUTA: Búsqueda de productos
@products_bp.route('/buscar')
def search_products():
    """Búsqueda de productos"""
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = 30
        
        if not query:
            return render_template('search_results.html', 
                                 products=[], 
                                 query=query,
                                 message='Ingresa un término de búsqueda')
        
        # Buscar productos que coincidan con el nombre o categoría
        products_query = Product.query.filter(
            db.or_(
                Product.nameProduct.ilike(f'%{query}%'),
                Product.category.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%')
            ),
            Product.status == 'Activo'
        )
        
        pagination = products_query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
        
        products = pagination.items
        
        # Convertir productos a formato para la template
        products_data = []
        for product in products:
            products_data.append({
                'id': product.idProduct,
                'name': product.nameProduct,
                'description': product.description or '',
                'price': float(product.price),
                'image_url': product.image or f'https://via.placeholder.com/300x400/f8f9fa/000?text={product.nameProduct}',
                'category': product.category,
                'stock': product.stock,
                'status': product.status
            })
        
        return render_template('search_results.html', 
                             products=products_data,
                             query=query,
                             current_page=page,
                             total_pages=pagination.pages,
                             has_next=pagination.has_next,
                             has_prev=pagination.has_prev)
                             
    except Exception as e:
        return render_template('error404.html'), 404