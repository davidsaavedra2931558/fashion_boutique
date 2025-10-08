from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
# ✅ ELIMINADA la importación circular: from app.models import Product
import os

# 👇 Agregar estas dos líneas
import pymysql
pymysql.install_as_MySQLdb()

# Inicializar extensiones PRIMERO
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # 🔒 CONFIGURACIÓN BÁSICA
    app.config['SECRET_KEY'] = 'tu-clave-secreta-muy-segura-aqui'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/fashion_boutique'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    # 📧 CONFIGURACIÓN DE GMAIL
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'davidsaavedrapinzon13@gmail.com'
    app.config['MAIL_PASSWORD'] = 'unxz cjlb vuwe ofzm'
    app.config['MAIL_DEFAULT_SENDER'] = 'davidsaavedrapinzon13@gmail.com'
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    # Importar y configurar user_loader DENTRO de create_app
    from app.models1 import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ✅ CORREGIDO: Crear tablas pero NO crear admin todavía (por el problema de created_at)
    with app.app_context():
        db.create_all()
        
        # ✅ SOLUCIÓN: Verificar si la columna created_at existe antes de crear el admin
        try:
            admin_user = db.session.query(User).filter_by(emailUser='admin@fashion.com').first()
            if not admin_user:
                admin = User(
                    nameUser='admin',
                    emailUser='admin@fashion.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Administrador creado: admin@fashion.com / admin123")
        except Exception as e:
            print(f"⚠️  No se pudo crear el admin: {e}")
            print("💡 Ejecuta: flask db migrate && flask db upgrade")
    
    # ✅ RUTA PRINCIPAL - Página de inicio con todos los productos
    @app.route('/')
    def index():
        # ✅ IMPORTAR Product DENTRO de la función para evitar circular import
        from app.models1 import Product
        
        page = request.args.get('page', 1, type=int)
        per_page = 30  # ✅ 30 productos por página (no 6)
        
        # Obtener productos con paginación
        products_query = Product.query.filter_by(status='Activo')
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
        
        return render_template('index.html', 
                             products=products_data,
                             current_page=page,
                             total_pages=pagination.pages,
                             has_next=pagination.has_next,
                             has_prev=pagination.has_prev)
    
    # ✅ CORREGIDO: Registrar blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.users_route import bp as users_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.products import products_bp
    from app.routes.cart import cart_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    
    return app