from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False, unique=True)
    documento = db.Column(db.String(50), nullable=True) # Para CPF ou RG
    ordens_servico = db.relationship('OrdemServico', backref='cliente', lazy=True)


# --- NOVO MODELO PARA O CATÁLOGO DE APARELHOS ---
class ModeloAparelho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50), nullable=False)
    nome_modelo = db.Column(db.String(100), nullable=False, unique=True)
    foto_vitrine_url = db.Column(db.String(255), nullable=True) # URL da imagem

class OrdemServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    os_number = db.Column(db.String(10), unique=True, nullable=False)
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo_aparelho.id'), nullable=False)
    modelo = db.relationship('ModeloAparelho')
    imei = db.Column(db.String(100))
    defeito_relatado = db.Column(db.Text, nullable=False)
    diagnostico_tecnico = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Em Análise')
    custo_pecas = db.Column(db.Float, default=0.0)
    valor_servico = db.Column(db.Float, default=0.0)
    metodo_pagamento = db.Column(db.String(50), nullable=True)
    valor_pago = db.Column(db.Float, nullable=True)
    data_pagamento = db.Column(db.DateTime, nullable=True)
    
    @property
    def valor_total(self):
        return (self.custo_pecas or 0.0) + (self.valor_servico or 0.0)
    

    checklist_items = db.relationship('ChecklistItem', backref='ordem_servico', cascade="all, delete-orphan")
    logs = db.relationship('LogOS', backref='ordem_servico', lazy=True, cascade="all, delete-orphan", order_by="desc(LogOS.timestamp)")
    fotos = db.relationship('FotoOS', backref='ordem_servico', lazy=True, cascade="all, delete-orphan")


class FotoOS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    os_id = db.Column(db.Integer, db.ForeignKey('ordem_servico.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_principal = db.Column(db.Boolean, default=False)

class LogOS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    os_id = db.Column(db.Integer, db.ForeignKey('ordem_servico.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    evento = db.Column(db.String(255), nullable=False)

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    os_id = db.Column(db.Integer, db.ForeignKey('ordem_servico.id'), nullable=False)
    item_nome = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    observacoes = db.Column(db.Text)

class Fornecedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, unique=True)
    contato = db.Column(db.String(100))
    telefone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    observacoes = db.Column(db.Text)
    frete = db.Column(db.Float, nullable=True)
    pedido_minimo = db.Column(db.Float, nullable=True)

