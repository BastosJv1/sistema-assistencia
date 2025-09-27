# app/portal/routes.py

from flask import Blueprint, render_template, request, flash
from app.models import OrdemServico, Cliente

portal_bp = Blueprint('portal', __name__, url_prefix='/cliente')

@portal_bp.route('/', methods=['GET', 'POST'])
def login_portal():
    if request.method == 'POST':
        os_number = request.form.get('os_number')
        telefone = request.form.get('telefone')
        
        os = OrdemServico.query.join(OrdemServico.cliente).filter(
            OrdemServico.os_number == os_number,
            Cliente.telefone == telefone
        ).first()
        
        if os:
            # A CORREÇÃO ESTÁ AQUI: Adicionamos 'show_nav=False'
            return render_template('portal/acompanhar.html', os=os, show_nav=False)
        else:
            flash('Ordem de Serviço ou Telefone não encontrado.', 'danger')
            # Também adicionamos aqui para o caso de falha no login
            return render_template('main/index.html', show_nav=False)

    # A página de login inicial já está correta, mas garantimos aqui também.
    return render_template('main/index.html', show_nav=False)