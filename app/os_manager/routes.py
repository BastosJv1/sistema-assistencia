from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
)
from flask_login import login_required
# Importação Única e Limpa de todos os modelos necessários
from app.models import db, Cliente, OrdemServico, ChecklistItem, LogOS, FotoOS, ModeloAparelho
from fpdf import FPDF
import random
from datetime import datetime
from io import BytesIO
from werkzeug.utils import secure_filename
import os
import uuid

os_manager_bp = Blueprint('os_manager', __name__)

CHECKLIST_PADRAO = [
    "Tela (Imagem/Manchas)", "Touch Screen", "Câmera Traseira", "Câmera Frontal",
    "Conector de Carga", "Wi-Fi / Bluetooth", "Alto-falante", "Auricular",
    "Microfone", "Botões Volume", "Botão Power"
]

def tratar_texto(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

class PDF(FPDF):
    def header(self):
        try:
            self.image('app/static/img/logo.png', 10, 8, 33)
        except FileNotFoundError:
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Oficina Inteligente', 0, False, 'L')
        self.set_font('Arial', 'B', 20)
        self.set_text_color(0, 174, 255)
        self.set_y(15)
        self.cell(0, 10, 'Ordem de Servico', 0, False, 'C')
        self.ln(25)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, False, 'C')

@os_manager_bp.route('/os/lista')
@login_required
def listar_os():
    lista_os = OrdemServico.query.order_by(OrdemServico.data_entrada.desc()).all()
    return render_template('os_manager/listar_os.html', lista_os=lista_os)

# --- NOVA ROTA DE API (EXEMPLO USANDO NOSSA CORREÇÃO) ---
# Esta rota retorna apenas os dados em formato JSON. Útil para dashboards dinâmicos no futuro.
@os_manager_bp.route('/api/os/lista')
@login_required
def api_listar_os():
    """ Rota de API que retorna todas as OS em formato JSON. """
    ordens_servico = OrdemServico.query.order_by(OrdemServico.data_entrada.desc()).all()
    
    # AQUI SIM, nós usamos a conversão para dicionário antes de retornar como JSON
    lista_os_dict = [os.to_dict() for os in ordens_servico]
    
    return jsonify(lista_os_dict)

@os_manager_bp.route('/os/nova', methods=['GET', 'POST'])
@login_required
def criar_os():
    if request.method == 'POST':
        cliente_telefone = request.form.get('cliente_telefone')
        cliente = Cliente.query.filter_by(telefone=cliente_telefone).first()
        if not cliente:
            cliente = Cliente(
                nome=request.form.get('cliente_nome'), 
                telefone=cliente_telefone,
                documento=request.form.get('cliente_documento')
            )
            db.session.add(cliente)
            db.session.commit()
        
        nova_os = OrdemServico(
            os_number=str(random.randint(10000, 99999)),
            cliente_id=cliente.id,
            modelo_id=request.form.get('modelo_id'), 
            imei=request.form.get('imei_aparelho'),
            defeito_relatado=request.form.get('defeito_relatado'))
        db.session.add(nova_os)
        db.session.commit()

        log_inicial = LogOS(os_id=nova_os.id, evento="Aparelho recebido em nossa bancada.")
        db.session.add(log_inicial)
        
        for item in CHECKLIST_PADRAO:
            item_slug = item.replace(" ", "_").replace("/", "").replace("(", "").replace(")", "").lower()
            status = request.form.get(f'check_{item_slug}')
            observacoes = request.form.get(f'obs_{item_slug}')
            check_item = ChecklistItem(os_id=nova_os.id, item_nome=item, status=status, observacoes=observacoes)
            db.session.add(check_item)
        
        db.session.commit()
        flash('Ordem de Serviço criada com sucesso!', 'success')
        return redirect(url_for('os_manager.ver_os', os_id=nova_os.id))
    
    modelos = ModeloAparelho.query.order_by(ModeloAparelho.nome_modelo).all()
    return render_template('os_manager/criar_os.html', checklist_padrao=CHECKLIST_PADRAO, modelos=modelos)

@os_manager_bp.route('/os/<int:os_id>', methods=['GET', 'POST'])
@login_required
def ver_os(os_id):
    os_obj = OrdemServico.query.get_or_404(os_id)
    if request.method == 'POST':
        form_name = request.form.get('form_name')
        if form_name == 'update_status':
            novo_status = request.form.get('status')
            if os_obj.status != novo_status:
                log_evento = LogOS(os_id=os_obj.id, evento=f"Status alterado para: {novo_status}")
                db.session.add(log_evento)
            os_obj.status = novo_status
            os_obj.custo_pecas = float(request.form.get('custo_pecas') or 0)
            os_obj.valor_servico = float(request.form.get('valor_servico') or 0)
            os_obj.diagnostico_tecnico = request.form.get('diagnostico_tecnico')
            db.session.commit()
            flash('Status e valores atualizados com sucesso!', 'success')
        elif form_name == 'faturar_os':
            os_obj.metodo_pagamento = request.form.get('metodo_pagamento')
            os_obj.valor_pago = float(request.form.get('valor_pago') or 0)
            os_obj.data_pagamento = datetime.utcnow()
            os_obj.status = 'Finalizado e Pago'
            log_faturamento = LogOS(os_id=os_obj.id, evento=f"Pagamento de R$ {os_obj.valor_pago:.2f} recebido via {os_obj.metodo_pagamento}.")
            log_status_final = LogOS(os_id=os_obj.id, evento="Status alterado para: Finalizado e Pago")
            db.session.add(log_faturamento)
            db.session.add(log_status_final)
            db.session.commit()
            flash(f'OS Nº {os_obj.os_number} faturada com sucesso!', 'success')
        elif form_name == 'upload_fotos':
            files = request.files.getlist('fotos')
            if not files or files[0].filename == '':
                flash('Nenhuma foto selecionada para upload.', 'warning')
            else:
                for file in files:
                    if file:
                        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        nova_foto = FotoOS(os_id=os_obj.id, filename=filename)
                        if not os_obj.fotos:
                            nova_foto.is_principal = True
                        db.session.add(nova_foto)
                db.session.commit()
                flash(f'{len(files)} foto(s) enviada(s) com sucesso!', 'success')
        return redirect(url_for('os_manager.ver_os', os_id=os_id))
    status_options = ['Em Análise', 'Aguardando Peça', 'Em Reparo', 'Aguardando Retirada', 'Finalizado', 'Finalizado e Pago']
    payment_options = ['PIX', 'Dinheiro', 'Cartão de Débito', 'Cartão de Crédito']
    return render_template('os_manager/ver_os.html', os=os_obj, status_options=status_options, payment_options=payment_options)

@os_manager_bp.route('/os/<int:os_id>/set_principal/<int:foto_id>')
@login_required
def set_foto_principal(os_id, foto_id):
    FotoOS.query.filter_by(os_id=os_id).update({FotoOS.is_principal: False})
    foto = FotoOS.query.get(foto_id)
    if foto:
        foto.is_principal = True
        db.session.commit()
        flash('Foto principal definida com sucesso!', 'success')
    return redirect(url_for('os_manager.ver_os', os_id=os_id))

@os_manager_bp.route('/os/<int:os_id>/pdf')
@login_required
def gerar_pdf_os(os_id):
    os = OrdemServico.query.get_or_404(os_id)
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, tratar_texto(f"OS Nº: {os.os_number} | Data de Entrada: {os.data_entrada.strftime('%d/%m/%Y')}"), 1, 1, 'C', True)
    pdf.ln(5)
    col_width = 95
    y_before_cols = pdf.get_y()
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(col_width, 7, tratar_texto('DADOS DO CLIENTE'), 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(col_width, 6, tratar_texto(f"Nome: {os.cliente.nome}"), 0, 1)
    pdf.cell(col_width, 6, tratar_texto(f"Telefone: {os.cliente.telefone}"), 0, 1)
    pdf.set_y(y_before_cols)
    pdf.set_x(10 + col_width)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(col_width, 7, tratar_texto('DADOS DO APARELHO'), 0, 1, 'L')
    pdf.set_x(10 + col_width)
    pdf.set_font('Arial', '', 10)
    pdf.cell(col_width, 6, tratar_texto(f"Modelo: {os.modelo.marca} {os.modelo.nome_modelo}"), 0, 1, 'L')
    pdf.set_x(10 + col_width)
    pdf.cell(col_width, 6, tratar_texto(f"IMEI: {os.imei}"), 0, 1, 'L')
    pdf.ln(10)
    
    # A CORREÇÃO DE INDENTAÇÃO ESTÁ AQUI
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, tratar_texto('DEFEITO RELATADO PELO CLIENTE'), 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_fill_color(245, 245, 245)
    pdf.multi_cell(0, 6, tratar_texto(os.defeito_relatado), border=1, align='L', fill=True)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, tratar_texto('CHECKLIST DE ENTRADA'), 0, 1)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(30, 30, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 7, 'Componente', 1, 0, 'C', True)
    pdf.cell(30, 7, 'Status', 1, 0, 'C', True)
    pdf.cell(100, 7, tratar_texto('Observações'), 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    fill = False
    for item in os.checklist_items:
        pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(240, 240, 240)
        pdf.cell(60, 6, tratar_texto(item.item_nome), 1, 0, 'L', True)
        pdf.cell(30, 6, tratar_texto(item.status), 1, 0, 'C', True)
        pdf.cell(100, 6, tratar_texto(item.observacoes or "-"), 1, 1, 'L', True)
        fill = not fill

    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 6, tratar_texto('TERMOS E CONDIÇÕES DO SERVIÇO'), 0, 1)
    pdf.set_font('Arial', '', 7)
    termos = 'A garantia de 90 dias cobre apenas o serviço executado e a peça trocada, excluindo-se danos por mau uso (queda, contato com líquido, etc.). A responsabilidade pela realização de backup de dados é exclusiva do cliente. Aparelhos não retirados em 90 dias serão considerados abandonados.'
    pdf.multi_cell(0, 4, tratar_texto(termos), border=1, align='L', fill=False)
    pdf.ln(15)

    col_width_sig = (pdf.w - pdf.l_margin - pdf.r_margin) / 2 - 5
    y_start_sig = pdf.get_y()

    pdf.cell(col_width_sig, 10, '_________________________', 0, 0, 'C')
    pdf.set_x(pdf.l_margin + col_width_sig + 10)
    pdf.cell(col_width_sig, 10, '_________________________', 0, 1, 'C')

    pdf.set_font('Arial', '', 8)
    pdf.set_y(y_start_sig + 6)
    pdf.cell(col_width_sig, 10, tratar_texto('João Victor Bastos Conceição'), 0, 0, 'C')
    pdf.set_x(pdf.l_margin + col_width_sig + 10)
    pdf.cell(col_width_sig, 10, tratar_texto(os.cliente.nome), 0, 1, 'C')

    pdf.set_y(y_start_sig + 10)
    pdf.cell(col_width_sig, 10, tratar_texto('CPF: 145.017.947-98'), 0, 0, 'C')
    pdf.set_x(pdf.l_margin + col_width_sig + 10)
    pdf.cell(col_width_sig, 10, tratar_texto(f"Doc: {os.cliente.documento or ''}"), 0, 1, 'C')
    
    buffer = BytesIO()
    buffer.write(pdf.output())
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=False,
        download_name=f'OS_{os.os_number}.pdf',
        mimetype='application/pdf'
    )

# --- NOVA ROTA PARA EXCLUIR ORDEM DE SERVIÇO ---
@os_manager_bp.route('/os/excluir/<int:os_id>', methods=['POST'])
@login_required
def excluir_os(os_id):
    """ Rota para excluir uma Ordem de Serviço e todos os seus dados relacionados. """
    os = OrdemServico.query.get_or_404(os_id)
    os_number = os.os_number # Guarda o número para a mensagem
    
    # Graças ao 'cascade="all, delete-orphan"' nos nossos modelos,
    # ao deletar a OS, o banco de dados deletará automaticamente todos os
    # checklists, logs e fotos associados a ela.
    db.session.delete(os)
    db.session.commit()
    
    flash(f'Ordem de Serviço Nº {os_number} foi excluída com sucesso.', 'danger')
    # Redireciona de volta para a lista principal de OSs
    return redirect(url_for('os_manager.listar_os'))