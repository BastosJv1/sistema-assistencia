from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas do banco de dados se elas não existirem
        db.create_all()
    # Inicia o servidor de desenvolvimento
    app.run(debug=True)