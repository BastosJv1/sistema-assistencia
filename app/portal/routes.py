# app/portal/routes.py

from flask import Blueprint, render_template, request, flash
from app.models import OrdemServico, Cliente

portal_bp = Blueprint('portal', __name__, url_prefix='/cliente')

# Dicionário para mapear o status do reparo a uma porcentagem de conclusão
STATUS_PROGRESSO = {
    'Em Análise': 15,
    'Aguardando Peça': 35,
    'Em Reparo': 65,
    'Aguardando Retirada': 90,
    'Finalizado': 100,
    'Finalizado e Pago': 100
}

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
            # --- NOVO ---
            # Calculamos a porcentagem de progresso aqui
            progress_percent = STATUS_PROGRESSO.get(os.status, 0)
            
            # Passamos a nova variável 'progress_percent' para o template
            return render_template('portal/acompanhar.html', os=os, show_nav=False, progress_percent=progress_percent)
        else:
            flash('Ordem de Serviço ou Telefone não encontrado.', 'danger')
            return render_template('main/index.html', show_nav=False)

    return render_template('main/index.html', show_nav=False)