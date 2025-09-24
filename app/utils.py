from flask_mail import Message
from flask import url_for, current_app
from app import mail

def send_reset_email(user):
    # SOLO PARA TESTING - NO ENVÍA EMAIL PERO GENERA EL TOKEN
    token = user.get_reset_token()
    reset_url = url_for('auth.reset_token', token=token, _external=True)
    print(f"🔐 ENLACE DE RECUPERACIÓN GENERADO: {reset_url}")
    
    # Para testing, siempre retorna True
    return True

def send_welcome_email(user):
    """Función alternativa para enviar email de bienvenida (backup)"""
    try:
        msg = Message(
            subject='🎉 ¡Bienvenido/a a Fashion Boutique!',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email]
        )
        
        msg.body = f"""
        FASHION BOUTIQUE - ¡Bienvenido/a!
        
        Hola {user.username},
        
        ¡Bienvenido/a a Fashion Boutique!
        
        Tu registro se ha completado exitosamente.
        
        Atentamente,
        El equipo de Fashion Boutique
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error enviando email de bienvenida: {e}")
        return False