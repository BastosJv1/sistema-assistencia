from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, ModeloAparelho

aparelho_bp = Blueprint('aparelho', __name__, url_prefix='/modelos')

@aparelho_bp.route('/')
@login_required
def listar_modelos():
    modelos = ModeloAparelho.query.order_by(ModeloAparelho.marca, ModeloAparelho.nome_modelo).all()
    return render_template('aparelho/listar_modelos.html', modelos=modelos)

@aparelho_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo_modelo():
    if request.method == 'POST':
        novo = ModeloAparelho(
            marca=request.form.get('marca'),
            nome_modelo=request.form.get('nome_modelo'),
            foto_vitrine_url=request.form.get('foto_vitrine_url')
        )
        db.session.add(novo)
        db.session.commit()
        flash('Novo modelo de aparelho cadastrado com sucesso!', 'success')
        return redirect(url_for('aparelho.listar_modelos'))
    return render_template('aparelho/formulario_modelo.html', titulo='Cadastrar Novo Modelo')

@aparelho_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_modelo(id):
    modelo = ModeloAparelho.query.get_or_404(id)
    if request.method == 'POST':
        modelo.marca = request.form.get('marca')
        modelo.nome_modelo = request.form.get('nome_modelo')
        modelo.foto_vitrine_url = request.form.get('foto_vitrine_url')
        db.session.commit()
        flash('Modelo atualizado com sucesso!', 'success')
        return redirect(url_for('aparelho.listar_modelos'))
    return render_template('aparelho/formulario_modelo.html', titulo='Editar Modelo', modelo=modelo)