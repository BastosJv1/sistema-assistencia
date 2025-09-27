from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Fornecedor

fornecedor_bp = Blueprint('fornecedor', __name__, url_prefix='/fornecedores')

@fornecedor_bp.route('/')
@login_required
def listar_fornecedores():
    fornecedores = Fornecedor.query.order_by(Fornecedor.nome).all()
    return render_template('fornecedor/listar_fornecedores.html', fornecedores=fornecedores)

@fornecedor_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo_fornecedor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        if Fornecedor.query.filter_by(nome=nome).first():
            flash(f'Fornecedor "{nome}" já existe.', 'warning')
            return redirect(url_for('fornecedor.listar_fornecedores'))
            
        novo = Fornecedor(
            nome=nome,
            contato=request.form.get('contato'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            website=request.form.get('website'),
            observacoes=request.form.get('observacoes'),
            # Salvando os novos campos
            frete=float(request.form.get('frete') or 0),
            pedido_minimo=float(request.form.get('pedido_minimo') or 0)
        )
        db.session.add(novo)
        db.session.commit()
        flash('Fornecedor cadastrado com sucesso!', 'success')
        return redirect(url_for('fornecedor.listar_fornecedores'))

    return render_template('fornecedor/formulario_fornecedor.html', titulo='Cadastrar Novo Fornecedor')

@fornecedor_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    if request.method == 'POST':
        fornecedor.nome = request.form.get('nome')
        fornecedor.contato = request.form.get('contato')
        fornecedor.telefone = request.form.get('telefone')
        fornecedor.email = request.form.get('email')
        fornecedor.website = request.form.get('website')
        fornecedor.observacoes = request.form.get('observacoes')
        # Salvando os novos campos na edição
        fornecedor.frete = float(request.form.get('frete') or 0)
        fornecedor.pedido_minimo = float(request.form.get('pedido_minimo') or 0)
        db.session.commit()
        flash('Fornecedor atualizado com sucesso!', 'success')
        return redirect(url_for('fornecedor.listar_fornecedores'))

    return render_template('fornecedor/formulario_fornecedor.html', titulo='Editar Fornecedor', fornecedor=fornecedor)

# --- NOVA ROTA PARA EXCLUIR ---
@fornecedor_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    nome_fornecedor = fornecedor.nome
    db.session.delete(fornecedor)
    db.session.commit()
    flash(f'Fornecedor "{nome_fornecedor}" excluído com sucesso.', 'danger')
    return redirect(url_for('fornecedor.listar_fornecedores'))