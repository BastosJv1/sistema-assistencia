from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Cliente

cliente_bp = Blueprint('cliente', __name__, url_prefix='/clientes')

@cliente_bp.route('/')
@login_required
def listar_clientes():
    clientes = Cliente.query.order_by(Cliente.nome).all()
    return render_template('cliente/listar_clientes.html', clientes=clientes)

@cliente_bp.route('/<int:cliente_id>')
@login_required
def ver_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return render_template('cliente/ver_cliente.html', cliente=cliente)