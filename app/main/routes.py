from flask import Blueprint, render_template
from app import db
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

# --- ADICIONE TODA ESTA NOVA FUNÇÃO ABAIXO ---
@main_bp.route('/inicializar-banco-de-dados-agora/um-segredo-para-o-setup')
def inicializar_db():
    try:
        db.create_all()
        return "<h1>SUCESSO!</h1><p>Todas as tabelas do banco de dados foram criadas. O sistema está pronto. LEMBRE-SE DE REMOVER ESTA ROTA IMEDIATAMENTE.</p>"
    except Exception as e:
        return f"<h1>ERRO!</h1><p>Ocorreu um erro ao criar as tabelas: {e}</p>"
    
    # --- ADICIONE TODA ESTA NOVA FUNÇÃO ABAIXO ---
@main_bp.route('/criar-meu-admin-agora/<string:username>/<string:password>')
def criar_admin_remotamente(username, password):
    """ Rota secreta para criar o primeiro usuário em produção sem shell. """
    user = User.query.filter_by(username=username).first()
    if not user:
        new_admin = User(username=username)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        return f"<h1>SUCESSO!</h1><p>Usuário '{username}' criado com a senha fornecida.</p><p><b>REMOVA ESTA ROTA DO SEU CÓDIGO AGORA.</b></p>"
    
    return f"<h1>AVISO!</h1><p>Usuário '{username}' já existe no banco de dados.</p><p><b>REMOVA ESTA ROTA DO SEU CÓDIGO AGORA.</b></p>"
