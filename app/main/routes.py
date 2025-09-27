from flask import Blueprint, render_template
from app.models import db, User


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html', show_nav=False)

# --- ADICIONE TODA ESTA FUNÇÃO ABAIXO ---
@main_bp.route('/setup-admin-inicial/um-segredo-bem-dificil-de-adivinhar')
def setup_admin():
    # Suas credenciais
    username_desejado = 'BastosJV'
    senha_desejada = '04031998'

    # Verifica se o usuário já existe para não criar duplicatas
    user = User.query.filter_by(username=username_desejado).first()
    if not user:
        new_admin = User(username=username_desejado)
        new_admin.set_password(senha_desejada)
        db.session.add(new_admin)
        db.session.commit()
        return f"<h1>Usuário '{username_desejado}' criado com sucesso!</h1><p>Pode fechar esta aba e fazer o login. LEMBRE-SE DE REMOVER ESTA ROTA AGORA.</p>"
    
    return f"<h1>Usuário '{username_desejado}' já existe.</h1><p>Pode fechar esta aba e fazer o login. LEMBRE-SE DE REMOVER ESTA ROTA AGORA.</p>"