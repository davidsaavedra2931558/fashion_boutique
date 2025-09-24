from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor inicia sesión primero', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Acceso restringido a administradores', 'danger')
            return redirect(url_for('users.profile'))
        return f(*args, **kwargs)
    return decorated_function