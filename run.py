from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Servidor iniciando en http://0.0.0.0:5000")
    print("📧 Email configurado:", app.config.get('MAIL_USERNAME'))
    
    # Obtener la URI de BD pero ocultar la contraseña por seguridad
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri:
        # Ocultar contraseña en los logs
        safe_db_uri = db_uri.split('@')[0].split(':')[0] + '://***:***@' + '@'.join(db_uri.split('@')[1:])
        print("🗄️ Base de datos:", safe_db_uri)
    else:
        print("🗄️ Base de datos: No configurada")
    
    app.run(debug=False, host='0.0.0.0', port=5000)