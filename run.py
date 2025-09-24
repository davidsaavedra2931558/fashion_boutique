from app import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Crear tablas 
        db.create_all()
        print("✅ Base de datos inicializada")
        print("📋 Tablas creadas:", list(db.metadata.tables.keys()))
    
    print("🚀 Servidor iniciando en http://localhost:5000")
    print("📧 Email configurado:", app.config.get('MAIL_USERNAME'))
    print("🗄️ Base de datos:", app.config.get('SQLALCHEMY_DATABASE_URI'))
    
    app.run(debug=True, host='0.0.0.0', port=5000)