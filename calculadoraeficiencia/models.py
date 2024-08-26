from calculadoraeficiencia import database
from datetime import datetime

class Cliente(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False)  # Removed unique=True
    telefone = database.Column(database.String, nullable=False)
    empresa = database.Column(database.String, nullable=False)
    cargo = database.Column(database.String, nullable=False)
    setor = database.Column(database.String, nullable=False)
    consent = database.Column(database.Boolean, nullable=False)
    data_cadastro = database.Column(database.DateTime, nullable=False, default=datetime.utcnow())

class ResultadoDiagnostico(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    cliente_id = database.Column(database.Integer, database.ForeignKey('cliente.id'), nullable=False)
    respostas = database.Column(database.JSON, nullable=False)  # Campo para armazenar as respostas e pesos
    pesototal = database.Column(database.Float, nullable=False)
    pesometa = database.Column(database.Float, nullable=False)
    pesoplano = database.Column(database.Float, nullable=False)
    pesoacao = database.Column(database.Float, nullable=False)
    data = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
