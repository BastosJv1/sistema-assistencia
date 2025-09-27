from app import create_app, db
from app.models import User
import getpass

# Cria uma instância do aplicativo Flask para ter acesso ao contexto
app = create_app()

# Usa o contexto do aplicativo para interagir com o banco de dados
with app.app_context():
    print("--- Assistente de Criação de Administrador ---")
    
    # Pede o nome de usuário desejado
    username_desejado = input("Digite o nome de usuário para o administrador (ex: admin): ")
    
    # Pede a senha de forma segura (não mostra na tela)
    senha_desejada = getpass.getpass("Digite a senha desejada: ")
    
    # Verifica se o usuário já existe
    user = User.query.filter_by(username=username_desejado).first()

    if user:
        # Se já existe, apenas atualiza a senha
        print(f"\nUsuário '{username_desejado}' já existe. Atualizando a senha...")
        user.set_password(senha_desejada)
    else:
        # Se não existe, cria um novo
        print(f"\nCriando novo usuário '{username_desejado}'...")
        user = User(username=username_desejado)
        user.set_password(senha_desejada)
        db.session.add(user)
    
    # Salva as alterações no banco de dados
    db.session.commit()
    print(f"\nOperação concluída com sucesso!")
    print(f"Agora você pode iniciar o servidor ('python run.py') e fazer login com o usuário '{username_desejado}'.")