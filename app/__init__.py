from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
import os
from urllib.parse import quote_plus

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
    
    # 🔒 CONFIGURACIÓN BÁSICA CON VARIABLES DE ENTORNO
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'superclave_secreta_para_flask')
    
    # ✅ CONFIGURACIÓN DE BD - Usando DATABASE_URL del .env
    database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://cesar:cesarc@isladigital.xyz:3311/f58_cesar')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10
        }
    }
    
    # 📧 CONFIGURACIÓN DE GMAIL CON VARIABLES DE ENTORNO
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER', 'davidsaavedrapinzon13@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS', 'unxz cjlb vuwe ofzm')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER', 'davidsaavedrapinzon13@gmail.com')
    
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
    
    # ✅ CORREGIDO: Manejo mejorado de la creación de tablas
    with app.app_context():
        try:
            # Probar conexión primero
            db.session.execute('SELECT 1')
            print("✅ Conexión a la base de datos exitosa!")
            
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas/verificadas correctamente")
            
            # Crear usuario admin si no existe
            try:
                admin_user = User.query.filter_by(emailUser='admin@fashion.com').first()
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
                else:
                    print("✅ Usuario administrador ya existe")
                    
            except Exception as admin_error:
                print(f"⚠️  No se pudo crear el admin: {admin_error}")
                db.session.rollback()
                
        except Exception as e:
            print(f"❌ Error al conectar con la base de datos: {e}")
            print("💡 Verifica:")
            print("   - Las credenciales de la base de datos")
            print("   - Que el servidor MySQL esté corriendo")
            print("   - Que la base de datos exista")
    
    # ✅ RUTA PRINCIPAL - Página de inicio con todos los productos
    @app.route('/')
    def index():
        try:
            # ✅ IMPORTAR Product DENTRO de la función para evitar circular import
            from app.models1 import Product
            
            page = request.args.get('page', 1, type=int)
            per_page = 30
            
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
                    'price': float(product.price) if product.price else 0,
                    'image_url': product.image or f'https://via.placeholder.com/300x400/f8f9fa/000?text={product.nameProduct.replace(" ", "+")}',
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
                                 
        except Exception as e:
            print(f"❌ Error en la ruta principal: {e}")
            return render_template('index.html', 
                                 products=[],
                                 current_page=1,
                                 total_pages=1,
                                 has_next=False,
                                 has_prev=False,
                                 error="Error al cargar productos")
    
    # ✅ MANEJO DE ERRORES
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # ✅ CORREGIDO: Registrar blueprints con manejo de errores
    try:
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
        
        print("✅ Todos los blueprints registrados correctamente")
        
    except ImportError as e:
        print(f"⚠️  Algunos blueprints no pudieron cargarse: {e}")
    except Exception as e:
        print(f"⚠️  Error al registrar blueprints: {e}")
    
    return app