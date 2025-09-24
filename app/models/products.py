from app import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'category'
    
    idCategory = db.Column(db.String(10), primary_key=True)  # C001, C002, etc.
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('Activa', 'Inactiva'), default='Activa')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con productos
    products = db.relationship('Product', backref='category_ref', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    __tablename__ = 'product'
    
    idProduct = db.Column(db.Integer, primary_key=True)
    nameProduct = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100))
    image = db.Column(db.String(500))
    status = db.Column(db.Enum('Activo', 'Inactivo'), default='Activo')
    details = db.Column(db.Text)
    size = db.Column(db.String(50))
    color = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Agregar relación foreign key (opcional pero recomendado)
    category_id = db.Column(db.String(10), db.ForeignKey('category.idCategory'))

    def __repr__(self):
        return f'<Product {self.nameProduct}>'