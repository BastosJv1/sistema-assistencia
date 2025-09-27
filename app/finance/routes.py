from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import db, OrdemServico
from sqlalchemy import func
from datetime import datetime
import pytz

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/dashboard')
@login_required
def dashboard():
    # --- Cálculos Gerais ---
    faturamento_total = db.session.query(func.sum(OrdemServico.valor_servico + OrdemServico.custo_pecas)).scalar() or 0
    custo_total = db.session.query(func.sum(OrdemServico.custo_pecas)).scalar() or 0
    lucro_total = faturamento_total - custo_total
    total_os_concluidas = OrdemServico.query.filter(OrdemServico.data_pagamento != None).count()

    # --- Novos KPIs de Performance ---
    ticket_medio = faturamento_total / total_os_concluidas if total_os_concluidas > 0 else 0
    lucro_medio_por_os = lucro_total / total_os_concluidas if total_os_concluidas > 0 else 0

    # --- Novos KPIs do Mês Atual ---
    hoje = datetime.utcnow()
    inicio_do_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    faturamento_mes_atual = db.session.query(func.sum(OrdemServico.valor_servico + OrdemServico.custo_pecas)).filter(OrdemServico.data_pagamento >= inicio_do_mes).scalar() or 0
    custo_mes_atual = db.session.query(func.sum(OrdemServico.custo_pecas)).filter(OrdemServico.data_pagamento >= inicio_do_mes).scalar() or 0
    lucro_mes_atual = faturamento_mes_atual - custo_mes_atual
    os_concluidas_mes = OrdemServico.query.filter(OrdemServico.data_pagamento >= inicio_do_mes).count()

    # Monta o dicionário de dados para enviar ao template
    kpis = {
        'geral': {
            'faturamento': f"R$ {faturamento_total:.2f}",
            'lucro': f"R$ {lucro_total:.2f}",
            'custo_pecas': f"R$ {custo_total:.2f}",
            'total_os_concluidas': total_os_concluidas
        },
        'performance': {
            'ticket_medio': f"R$ {ticket_medio:.2f}",
            'lucro_medio_por_os': f"R$ {lucro_medio_por_os:.2f}"
        },
        'mes_atual': {
            'faturamento': f"R$ {faturamento_mes_atual:.2f}",
            'lucro': f"R$ {lucro_mes_atual:.2f}",
            'os_concluidas': os_concluidas_mes
        }
    }
    
    data_atual = datetime.now(pytz.timezone('America/Sao_Paulo'))

    return render_template('finance/dashboard.html', kpis=kpis, data_atual=data_atual)