from flask import Blueprint, jsonify, request, render_template, flash
from flask_login import login_required, current_user
from app import db
from app.models import CartItem, Product
from datetime import datetime

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
@login_required
def view_cart():
    try:
        cart_items = current_user.get_cart()
        total = 0
        cart_data = []
        
        for item in cart_items:
            # Asegúrate de que el producto existe
            if item.product:
                product_total = float(item.product.price) * item.quantity
                total += product_total
                
                cart_data.append({
                    'id': item.idCartItem,
                    'product_id': item.product.idProduct,
                    'name': item.product.nameProduct,
                    'price': float(item.product.price),
                    'quantity': item.quantity,
                    'image': item.product.image,
                    'subtotal': product_total
                })
            else:
                # Si el producto fue eliminado, elimina el item del carrito
                db.session.delete(item)
                db.session.commit()
        
        return render_template('cart.html', cart_items=cart_data, total=total)
    
    except Exception as e:
        flash('Error al cargar el carrito', 'danger')
        return render_template('cart.html', cart_items=[], total=0)

@cart_bp.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Verificar si el producto existe
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        # Verificar si el producto ya está en el carrito
        existing_item = CartItem.query.filter_by(
            idUser=current_user.idUser, 
            idProduct=product_id
        ).first()
        
        if existing_item:
            # Verificar stock disponible
            if existing_item.quantity + quantity > product.stock:
                return jsonify({'success': False, 'message': 'No hay suficiente stock disponible'})
            
            existing_item.quantity += quantity
        else:
            # Verificar stock disponible
            if quantity > product.stock:
                return jsonify({'success': False, 'message': 'No hay suficiente stock disponible'})
            
            new_item = CartItem(
                idUser=current_user.idUser,
                idProduct=product_id,
                quantity=quantity
            )
            db.session.add(new_item)
        
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Producto agregado al carrito',
            'cart_count': current_user.get_cart_count()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al agregar al carrito: ' + str(e)})

@cart_bp.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart_item():
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        
        if quantity <= 0:
            return remove_from_cart()
        
        item = CartItem.query.get(item_id)
        if item and item.idUser == current_user.idUser:
            # Verificar stock disponible
            if quantity > item.product.stock:
                return jsonify({'success': False, 'message': 'No hay suficiente stock disponible'})
            
            item.quantity = quantity
            db.session.commit()
            return jsonify({'success': True, 'message': 'Carrito actualizado'})
        
        return jsonify({'success': False, 'message': 'Item no encontrado'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al actualizar el carrito'})

@cart_bp.route('/api/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        
        item = CartItem.query.get(item_id)
        if item and item.idUser == current_user.idUser:
            db.session.delete(item)
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': 'Producto eliminado del carrito',
                'cart_count': current_user.get_cart_count()
            })
        
        return jsonify({'success': False, 'message': 'Item no encontrado'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al eliminar el producto'})

@cart_bp.route('/api/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    try:
        CartItem.query.filter_by(idUser=current_user.idUser).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Carrito vaciado'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al vaciar el carrito'})

@cart_bp.route('/api/cart/count')
@login_required
def get_cart_count():
    try:
        count = current_user.get_cart_count()
        return jsonify({'success': True, 'count': count})
    
    except Exception as e:
        return jsonify({'success': False, 'count': 0})