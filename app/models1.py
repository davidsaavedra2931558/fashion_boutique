from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    idUser = db.Column(db.Integer, primary_key=True)
    nameUser = db.Column(db.String(50), unique=True, nullable=False)
    emailUser = db.Column(db.String(120), unique=True, nullable=False)
    passwordUser = db.Column(db.String(255), nullable=False)
    
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    verification_code = db.Column(db.String(6), nullable=True)
    verification_code_expiration = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con el carrito
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def get_id(self):
        return str(self.idUser)

    def set_password(self, password):
        self.passwordUser = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.passwordUser, password)
    
    def is_administrator(self):
        return self.is_admin
    
    def get_role_display(self):
        return "Administrador" if self.is_admin else "Usuario"
    
    # Métodos para el carrito
    def get_cart(self):
        return CartItem.query.filter_by(idUser=self.idUser).all()
    
    def get_cart_count(self):
        return CartItem.query.filter_by(idUser=self.idUser).count()

    def __repr__(self):
        return f'<User {self.nameUser}>'

# Modelo para invitaciones
class Invitation(db.Model):
    __tablename__ = 'invitation'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Invitation {self.email}>'

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

# Modelo para items del carrito
class CartItem(db.Model):
    __tablename__ = 'cart_item'
    idCartItem = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    idProduct = db.Column(db.Integer, db.ForeignKey('product.idProduct'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con producto
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

# Tablas para el dashboard
class Product(db.Model):
    __tablename__ = 'product'
    idProduct = db.Column(db.Integer, primary_key=True)
    nameProduct = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100))
    image = db.Column(db.String(255))
    status = db.Column(db.Enum('Activo', 'Inactivo'), default='Activo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.nameProduct}>'

class Category(db.Model):
    __tablename__ = 'category'
    idCategory = db.Column(db.Integer, primary_key=True)
    nameCategory = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('Activa', 'Inactiva'), default='Activa')

    def __repr__(self):
        return f'<Category {self.nameCategory}>'

class Order(db.Model):
    __tablename__ = 'orders'
    idOrder = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    totalAmount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('Pendiente', 'Procesando', 'Enviado', 'Completado', 'Cancelado'), default='Pendiente')
    orderDate = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.idOrder}>'

class OrderDetail(db.Model):
    __tablename__ = 'order_detail'
    idOrderDetail = db.Column(db.Integer, primary_key=True)
    idOrder = db.Column(db.Integer, db.ForeignKey('orders.idOrder'))
    idProduct = db.Column(db.Integer, db.ForeignKey('product.idProduct'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    order = db.relationship('Order', backref=db.backref('details', lazy=True))
    product = db.relationship('Product', backref=db.backref('order_details', lazy=True))

    def __repr__(self):
        return f'<OrderDetail {self.idOrderDetail}>'

# NUEVOS MODELOS PARA FACTURAS FÍSICAS
class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    idInvoice = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Información del cliente
    customer_name = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.String(50))
    customer_email = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.Text)
    
    # Información de pago
    payment_method = db.Column(db.String(50), nullable=False)
    payment_details = db.Column(db.Text)
    cash_received = db.Column(db.Numeric(10, 2), default=0)
    change_given = db.Column(db.Numeric(10, 2), default=0)
    
    # Totales
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    total_discount = db.Column(db.Numeric(10, 2), default=0)
    taxes = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Estado y metadatos
    status = db.Column(db.Enum('Activa', 'Anulada', 'Enviada'), default='Activa')
    email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con los items de la factura
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def to_dict(self):
        return {
            'id': self.idInvoice,
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date.isoformat(),
            'customer_name': self.customer_name,
            'customer_id': self.customer_id,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'customer_address': self.customer_address,
            'payment_method': self.payment_method,
            'payment_details': self.payment_details,
            'cash_received': float(self.cash_received) if self.cash_received else 0,
            'change_given': float(self.change_given) if self.change_given else 0,
            'subtotal': float(self.subtotal),
            'total_discount': float(self.total_discount),
            'taxes': float(self.taxes),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'email_sent': self.email_sent,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    idInvoiceItem = db.Column(db.Integer, primary_key=True)
    idInvoice = db.Column(db.Integer, db.ForeignKey('invoices.idInvoice'), nullable=False)
    idProduct = db.Column(db.Integer, db.ForeignKey('product.idProduct'))
    product_name = db.Column(db.String(255), nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=0)  # Porcentaje de descuento
    discount_amount = db.Column(db.Numeric(10, 2), default=0)  # Monto del descuento
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relación con producto (opcional, para productos del catálogo)
    product = db.relationship('Product', backref=db.backref('invoice_items', lazy=True))
    
    def __repr__(self):
        return f'<InvoiceItem {self.product_name} x {self.quantity}>'
    
    def to_dict(self):
        return {
            'id': self.idInvoiceItem,
            'product_name': self.product_name,
            'product_price': float(self.product_price),
            'quantity': self.quantity,
            'discount': float(self.discount),
            'discount_amount': float(self.discount_amount),
            'subtotal': float(self.subtotal),
            'idProduct': self.idProduct
        }

# Modelo para ventas diarias (opcional, para reportes)
class DailySale(db.Model):
    __tablename__ = 'daily_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_date = db.Column(db.Date, nullable=False, index=True)
    total_sales = db.Column(db.Numeric(10, 2), default=0)
    total_invoices = db.Column(db.Integer, default=0)
    average_ticket = db.Column(db.Numeric(10, 2), default=0)
    
    def __repr__(self):
        return f'<DailySale {self.sale_date}>'

# Modelo para métodos de pago (opcional, para estadísticas)
class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<PaymentMethod {self.name}>'

# ============================
# NUEVOS MODELOS PARA COLORES, TALLAS Y VARIANTES
# ============================

class Color(db.Model):
    __tablename__ = 'colors'
    
    idColor = db.Column(db.Integer, primary_key=True)
    nameColor = db.Column(db.String(50), nullable=False, unique=True)
    hex_code = db.Column(db.String(7), default='#6c757d')
    status = db.Column(db.Enum('Activo', 'Inactivo'), default='Activo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Color {self.nameColor}>'

class Size(db.Model):
    __tablename__ = 'sizes'
    
    idSize = db.Column(db.Integer, primary_key=True)
    nameSize = db.Column(db.String(20), nullable=False, unique=True)
    category = db.Column(db.String(50))
    status = db.Column(db.Enum('Activo', 'Inactivo'), default='Activo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Size {self.nameSize}>'

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    
    idVariant = db.Column(db.Integer, primary_key=True)
    idProduct = db.Column(db.Integer, db.ForeignKey('product.idProduct'), nullable=False)
    idColor = db.Column(db.Integer, db.ForeignKey('colors.idColor'))
    idSize = db.Column(db.Integer, db.ForeignKey('sizes.idSize'))
    sku = db.Column(db.String(100), unique=True, nullable=False)
    price_extra = db.Column(db.Numeric(10, 2), default=0)
    stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=5)
    status = db.Column(db.Enum('Activo', 'Inactivo'), default='Activo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    product = db.relationship('Product', backref=db.backref('variants', lazy=True))
    color = db.relationship('Color', backref=db.backref('variants', lazy=True))
    size = db.relationship('Size', backref=db.backref('variants', lazy=True))

    def __repr__(self):
        return f'<ProductVariant {self.sku}>'

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    
    idImage = db.Column(db.Integer, primary_key=True)
    idProduct = db.Column(db.Integer, db.ForeignKey('product.idProduct'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref=db.backref('additional_images', lazy=True))

    def __repr__(self):
        return f'<ProductImage {self.idImage}>'