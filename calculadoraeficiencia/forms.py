from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError
import re

class FormLead(FlaskForm):
    nome = StringField("Nome:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired(), Email(message="Por favor, insira um e-mail válido.")])
    telefone = StringField("Telefone:", validators=[DataRequired()])
    empresa = StringField("Empresa:", validators=[DataRequired()])
    cargo = StringField("Cargo:", validators=[DataRequired()])
    setor = SelectField("Setor:", choices=[('Execução Obra', 'Execução Obra'), ('Orçamento', 'Orçamento'), ('Planejamento', 'Planejamento'), ('Projetos', 'Projetos'), ('Compras/Suprimentos', 'Compras/Suprimentos'),
                                           ('Financeiro', 'Financeiro'), ('Diretoria', 'Diretoria'), ('Outros', 'Outros')],
                        validators=[DataRequired()])
    consent = BooleanField("Eu concordo em receber comunicações da Tático e parceiros.")
    botao_enviar = SubmitField("CALCULAR A EFICIÊNCIA")

    def validate_telefone(self, telefone):
        # Regex para validar telefone no formato (XX) XXXXX-XXXX, (XX) XXXX-XXXX ou XXXXXXXXXXX
        pattern = re.compile(r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$")
        if not pattern.match(telefone.data):
            raise ValidationError("Por favor, insira um número de telefone válido")
