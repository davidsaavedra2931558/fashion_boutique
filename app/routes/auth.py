from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db, mail
from app.models import User  # ← Importar User (singular)
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import random
import string
from datetime import datetime, timedelta

# Configurar logging
logger = logging.getLogger(__name__)

# Crear el Blueprint
bp = Blueprint('auth', __name__)

# FUNCIÓN PARA ENVIAR EMAIL DE BIENVENIDA
def send_welcome_email(user):
    try:
        msg = Message(
            subject='🎉 ¡Bienvenido/a a Fashion Boutique!',
            sender=('Fashion Boutique', 'noreply.fashionboutique@gmail.com'),
            recipients=[user.emailUser]  # ← emailUser en lugar de email
        )

        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: #000000;
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 30px;
                }}
                .welcome-text {{
                    font-size: 18px;
                    color: #333;
                    line-height: 1.6;
                }}
                .features {{
                    margin: 20px 0;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }}
                .features li {{
                    margin: 10px 0;
                }}
                .cta-button {{
                    display: inline-block;
                    background: #4A90E2;  /* Cambiado a azul claro */
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                    transition: background-color 0.3s ease;
                }}
                .cta-button:hover {{
                    background: #357ABD;  /* Azul más oscuro al pasar el mouse */
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>FASHION BOUTIQUE</h1>
                </div>
                
                <div class="content">
                    <h2>¡Hola {user.nameUser}!</h2>  <!-- ← nameUser en lugar de username -->
                    
                    <div class="welcome-text">
                        <p>Nos alegra enormemente darte la bienvenida a <strong>Fashion Boutique</strong>.</p>
                        <p>Tu registro se ha completado exitosamente y ahora formas parte de nuestra comunidad de moda.</p>
                    </div>
                    
                    <div class="features">
                        <h3>✨ Lo que puedes disfrutar:</h3>
                        <ul>
                            <li>📦 Productos de moda exclusivos y tendencias actuales</li>
                            <li>🎁 Ofertas especiales y descuentos para miembros</li>
                            <li>🚚 Envíos rápidos y seguros</li>
                            <li>⭐ Atención personalizada 24/7</li>
                            <li>💝 Recomendaciones basadas en tu estilo</li>
                        </ul>
                    </div>
                    
                    <p>Estamos aquí para ayudarte a encontrar tu estilo único.</p>
                    
                    <center>
                        <a href="{url_for('auth.login', _external=True)}" class="cta-button">
                            Comenzar a comprar
                        </a>
                    </center>
                    
                    <p>Si tienes alguna pregunta, no dudes en contactarnos en cualquier momento.</p>
                    
                    <p>¡Bienvenido/a a la familia Fashion Boutique! 🛍️</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Fashion Boutique. Todos los derechos reservados.</p>
                    <p>Este es un email automático, por favor no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.body = f"""
        FASHION BOUTIQUE - ¡Bienvenido/a!
        
        Hola {user.nameUser},
        
        ¡Bienvenido/a a Fashion Boutique!
        
        Tu registro se ha completado exitosamente. Ahora puedes:
        - Explorar nuestra colección exclusiva
        - Disfrutar de ofertas especiales
        - Recibir envíos rápidos y seguros
        - Obtener atención personalizada
        
        Inicia sesión aquí: {url_for('auth.login', _external=True)}
        
        Si tienes preguntas, estamos aquí para ayudarte.
        
        ¡Gracias por unirte a nosotros!
        
        Atentamente,
        El equipo de Fashion Boutique
        """

        mail.send(msg)
        logger.info(f"✅ Email de bienvenida enviado a {user.emailUser}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email de bienvenida: {str(e)}")
        return False

# FUNCIÓN PARA ENVIAR EMAIL DE VERIFICACIÓN
def send_verification_email(user, verification_code):
    try:
        msg = Message(
            subject='🔐 Código de Verificación - Fashion Boutique',
            sender=('Fashion Boutique', 'noreply.fashionboutique@gmail.com'),
            recipients=[user.emailUser]  # ← emailUser en lugar de email
        )

        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: #000000;
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 30px;
                }}
                .code-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .verification-code {{
                    display: inline-block;
                    background: #4A90E2;  /* Cambiado a azul claro */
                    color: white;
                    font-size: 32px;
                    font-weight: bold;
                    padding: 15px 30px;
                    border-radius: 8px;
                    letter-spacing: 5px;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>FASHION BOUTIQUE</h1>
                </div>
                
                <div class="content">
                    <h2>Hola {user.nameUser},</h2>  <!-- ← nameUser en lugar de username -->
                    <p>Has solicitado restablecer tu contraseña en <strong>Fashion Boutique</strong>. 
                       Usa el siguiente código de verificación para continuar:</p>
                    
                    <div class="code-container">
                        <div class="verification-code">{verification_code}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Importante de seguridad:</strong>
                        <ul>
                            <li>Este código expirará en <strong>10 minutos</strong></li>
                            <li>No compartas este código con nadie</li>
                            <li>Si no solicitaste este cambio, ignora este email</li>
                        </ul>
                    </div>
                    
                    <p>Ingresa este código en la página de verificación para completar el proceso.</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Fashion Boutique. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.body = f"""
        FASHION BOUTIQUE - Código de Verificación
        
        Hola {user.nameUser},
        
        Tu código de verificación es: {verification_code}
        
        Este código expirará en 10 minutos.
        
        Atentamente,
        El equipo de Fashion Boutique
        """

        mail.send(msg)
        logger.info(f"✅ Email de verificación enviado a {user.emailUser}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email: {str(e)}")
        return False

# GENERAR CÓDIGO DE VERIFICACIÓN
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# RUTAS DE AUTENTICACIÓN
@bp.route('/')
def home():
    """Página principal - Muestra home.html"""
    return render_template('home.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # ✅ Redirigir según el rol
        if current_user.is_admin:
            return redirect(url_for('users.admin_dashboard'))
        else:
            return redirect(url_for('users.profile'))
    
    if request.method == 'POST':
        nameUser = request.form.get('nameUser')  # ← nameUser en lugar de username
        passwordUser = request.form.get('passwordUser')  # ← passwordUser en lugar de password
        
        user = User.query.filter_by(nameUser=nameUser).first()  # ← nameUser
        
        if user and user.check_password(passwordUser):  # ← passwordUser
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            
            # ✅ Redirigir según el rol después del login
            if user.is_admin:
                return redirect(url_for('users.admin_dashboard'))
            else:
                return redirect(url_for('users.profile'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # ✅ Redirigir según el rol
        if current_user.is_admin:
            return redirect(url_for('users.admin_dashboard'))
        else:
            return redirect(url_for('users.profile'))
    
    if request.method == 'POST':
        nameUser = request.form.get('nameUser')  # ← nameUser
        emailUser = request.form.get('emailUser')  # ← emailUser
        passwordUser = request.form.get('passwordUser')  # ← passwordUser
        confirmPassword = request.form.get('confirmPassword')
        
        if passwordUser != confirmPassword:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(emailUser=emailUser).first():  # ← emailUser
            flash('El email ya está registrado', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(nameUser=nameUser).first():  # ← nameUser
            flash('El nombre de usuario ya existe', 'danger')
            return render_template('register.html')
        
        try:
            # ✅ Crear nuevo usuario con los nombres de campo correctos
            new_user = User(
                nameUser=nameUser,
                emailUser=emailUser,
                is_admin=False
            )
            new_user.set_password(passwordUser)  # ← passwordUser
            
            db.session.add(new_user)
            db.session.commit()
            
            # ✅ ENVIAR EMAIL DE BIENVENIDA
            if send_welcome_email(new_user):
                logger.info(f"Email de bienvenida enviado a {new_user.emailUser}")
            else:
                logger.warning(f"No se pudo enviar email de bienvenida a {new_user.emailUser}")
            
            flash(f'¡Bienvenido/a {nameUser}! Tu cuenta ha sido creada exitosamente. Revisa tu email para más detalles.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la cuenta: {str(e)}', 'danger')
    
    return render_template('register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.home'))

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(emailUser=email).first()  # ← emailUser
        
        if user:
            try:
                verification_code = generate_verification_code()
                user.verification_code = verification_code
                user.verification_code_expiration = datetime.utcnow() + timedelta(minutes=10)
                
                db.session.commit()
                
                if send_verification_email(user, verification_code):
                    session['reset_email'] = email
                    flash('Código de verificación enviado a tu email', 'success')
                    return redirect(url_for('auth.verify_reset_code'))
                else:
                    flash('Error al enviar el email', 'danger')
                    
            except Exception as e:
                db.session.rollback()
                flash('Error al procesar la solicitud', 'danger')
        else:
            flash('Si el email existe, recibirás un código de verificación', 'info')
    
    return render_template('reset_request.html')

@bp.route('/verify_reset_code', methods=['GET', 'POST'])
def verify_reset_code():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('auth.reset_request'))
    
    user = User.query.filter_by(emailUser=email).first()  # ← emailUser
    if not user:
        flash('Solicitud inválida', 'danger')
        return redirect(url_for('auth.reset_request'))
    
    if request.method == 'POST':
        code = request.form.get('verification_code')
        
        if user.verification_code == code and user.verification_code_expiration > datetime.utcnow():
            session['verified_email'] = email
            flash('Código verificado correctamente', 'success')
            return redirect(url_for('auth.reset_token'))
        else:
            flash('Código inválido o expirado', 'danger')
    
    return render_template('verify_code.html', email=email)

@bp.route('/reset_token', methods=['GET', 'POST'])
def reset_token():
    email = session.get('verified_email')
    if not email:
        return redirect(url_for('auth.reset_request'))
    
    user = User.query.filter_by(emailUser=email).first()  # ← emailUser
    if not user:
        flash('Solicitud inválida', 'danger')
        return redirect(url_for('auth.reset_request'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
        else:
            # ✅ Usar el método set_password()
            user.set_password(new_password)
            user.verification_code = None
            user.verification_code_expiration = None
            
            db.session.commit()
            
            session.pop('reset_email', None)
            session.pop('verified_email', None)
            
            flash('Contraseña restablecida correctamente', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('reset_token.html')

@bp.route('/test')
def test():
    return "✅ ¡La aplicación funciona correctamente!"

    