from flask import render_template, url_for, flash, redirect, request, session, send_file
from calculadoraeficiencia import app, database, mail
from calculadoraeficiencia.forms import FormLead
from calculadoraeficiencia.models import Cliente, ResultadoDiagnostico
from sqlalchemy.exc import IntegrityError
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from flask_mail import Message
import json

# Registre a fonte Montserrat
pdfmetrics.registerFont(TTFont('Montserrat', 'fonts/Montserrat-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Montserrat-Bold', 'fonts/Montserrat-Bold.ttf'))


@app.route("/", methods=["GET", "POST"])
def homepage():
    formlead = FormLead()
    if formlead.validate_on_submit():
        novo_cliente = Cliente(
            nome=formlead.nome.data,
            email=formlead.email.data,
            telefone=formlead.telefone.data,
            empresa=formlead.empresa.data,
            cargo=formlead.cargo.data,
            setor=formlead.setor.data,
            consent=formlead.consent.data,
        )
        try:
            database.session.add(novo_cliente)
            database.session.commit()
            session['cliente_id'] = novo_cliente.id  # Armazena o cliente_id na sessão
            return redirect(url_for('graumaturidade'))
        except IntegrityError:
            database.session.rollback()
            flash("Erro ao salvar os dados!", "danger")

    return render_template("index.html", form=formlead)


@app.route("/graueficiencia")
def graumaturidade():
    return render_template("graumaturidade.html")


@app.route("/diagnosticoeficiencia")
def diagnosticomaturidade():
    cliente_id = session.get('cliente_id')
    return render_template("diagnosticomaturidade.html", cliente_id=cliente_id)


@app.route("/resultado", methods=["GET"])
def resultado():
    cliente_id = session.get('cliente_id')
    if not cliente_id:
        flash("Erro: Nenhum cliente encontrado na sessão.", "danger")
        return redirect(url_for('homepage'))

    resultado = ResultadoDiagnostico.query.filter_by(cliente_id=cliente_id).first()
    if not resultado:
        flash("Erro: Nenhum diagnóstico encontrado para o cliente.", "danger")
        return redirect(url_for('diagnosticomaturidade'))



    return render_template("resultado.html", resultado=resultado)


@app.route("/salvar_resultado", methods=["POST"])
def salvar_resultado():
    cliente_id = request.form.get("cliente_id")
    if not cliente_id or not cliente_id.isdigit():
        flash("ID do cliente é inválido!", "danger")
        return redirect(url_for('diagnosticomaturidade'))

    # Capturando o JSON das respostas
    responses = request.form.get("respostas")
    if responses:
        responses = json.loads(responses)

        # Renomeando as chaves "question" para "questão"
        responses = {key.replace("question", "questão"): value for key, value in responses.items()}

    # Função auxiliar para converter em float, substituindo None por 0
    def safe_float(value):
        return float(value) if value is not None and value != '' else 0.0

    # Capturando e validando os valores de peso total e de cada seção
    pesototal = safe_float(request.form.get("pesototal"))
    pesometa = safe_float(request.form.get("pesometa"))
    pesoplano = safe_float(request.form.get("pesoplano"))
    pesoacao = safe_float(request.form.get("pesoacao"))

    novo_diagnostico = ResultadoDiagnostico(
        cliente_id=int(cliente_id),
        pesototal=pesototal,
        pesometa=pesometa,
        pesoplano=pesoplano,
        pesoacao=pesoacao,
        respostas=responses  # Usando o dicionário com as chaves atualizadas
    )

    database.session.add(novo_diagnostico)
    database.session.commit()

    return redirect(url_for('resultado'))


@app.route("/gerar_pdf_reportlab")
def gerar_pdf_reportlab():
    cliente_id = session.get('cliente_id')
    if not cliente_id:
        flash("Erro: Nenhum cliente encontrado na sessão.", "danger")
        return redirect(url_for('homepage'))

    resultado = ResultadoDiagnostico.query.filter_by(cliente_id=cliente_id).first()
    if not resultado:
        flash("Erro: Nenhum diagnóstico encontrado para o cliente.", "danger")
        return redirect(url_for('diagnosticomaturidade'))

    # Recuperar o nome da empresa
    cliente = Cliente.query.get(cliente_id)
    nome_empresa = cliente.empresa if cliente.empresa else "Empresa"

    # Criar o nome do arquivo PDF
    nome_arquivo_pdf = f"{nome_empresa} - Eficiência em Gestão de Custos.pdf"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='Montserrat-Bold',
        fontSize=18,
        spaceAfter=12,
    )

    default_style = ParagraphStyle(
        'Default',
        parent=styles['Normal'],
        fontName='Montserrat',
        fontSize=12,
        spaceAfter=6,
    )

    bold_style = ParagraphStyle(
        'Bold',
        parent=styles['Normal'],
        fontName='Montserrat-Bold',
        fontSize=12,
        spaceAfter=6,
    )

    elements = []

    title = Paragraph("Resultado do Diagnóstico de Eficiência", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    dicionario_perguntas = {
        "1": "Qual a média de obras simultâneas com que a empresa atua?",
        "2": "Qual a média de lançamentos por ano da empresa?",
        "3": "Como são realizadas as viabilidades para novos empreendimentos?",
        "4": "Quantos orçamentos, em média, são realizados do início da concepção do empreendimento até o final da obra?",
        "5": "Em que fase são contratados os projetistas responsáveis pelos projetos complementares (Hidrossanitário, Preventivo, Elétrico...)?",
        "6": "Qual o ERP utilizado pela empresa?",
        "7": "A empresa trabalha com a metodologia BIM?",
        "8": "Está em qual fase de implantação?",
        "9": "Já conhece ou utiliza a Linha de Balanço (LOB)?",
        "10": "Utilizam outras soluções? (Permite mais de uma resposta)",
        "11": "Como ocorre o processo de orçamentação da empresa atualmente?",
        "12": "Como ocorre o processo de planejamento da empresa atualmente?",
        "13": "Todos os departamentos possuem acesso às informações financeiras/de custos das obras?",
        "14": "Como são realizadas as compras para as obras?",
        "15": "Realizam análises físico-financeiras?",
        "16": "Realizam as análises com qual frequência?",
        "17": "Qual o nível de envolvimento da diretoria no acompanhamento (físico e/ou financeiro) durante a execução das obras?",
    }

    for question_key, data in resultado.respostas.items():
        question_number = question_key.replace("questão", "")
        question_text = dicionario_perguntas.get(question_number, f"Questão {question_number}")

        # Combine o número da questão com o texto da pergunta
        full_question_text = f"{question_number}. {question_text}"

        if isinstance(data['resposta'], list):
            resposta_text = f"Respostas: {', '.join(data['resposta'])}"
        else:
            resposta_text = f"Resposta: {data['resposta']}"

        peso_text = f"Peso: {data['peso']:.2f}"

        elements.append(Paragraph(full_question_text, bold_style))  # Pergunta em negrito
        elements.append(Paragraph(resposta_text, default_style))  # Resposta em estilo normal
        elements.append(Paragraph(peso_text, default_style))  # Peso em estilo normal
        elements.append(Spacer(1, 12))

    # Calcular os valores normalizados para cada categoria na escala de 0 a 10
    nota_meta = (resultado.pesometa / 2.45) * 10
    nota_plano = (resultado.pesoplano / 4.85) * 10
    nota_acao = (resultado.pesoacao / 2.7) * 10

    titulo_notas = Paragraph("Notas por categoria", bold_style)
    elements.append(titulo_notas)

    # Adicionando as notas de Meta, Plano e Ação no PDF, uma abaixo da outra
    meta = Paragraph(f"Nota Meta: {nota_meta:.2f}", bold_style)
    plano = Paragraph(f"Nota Plano: {nota_plano:.2f}", bold_style)
    acao = Paragraph(f"Nota Ação: {nota_acao:.2f}", bold_style)

    # Adicionar um espaçamento entre as notas, se necessário
    elements.append(Spacer(1, 12))  # Adiciona um pequeno espaço antes das notas
    elements.append(meta)
    elements.append(plano)
    elements.append(acao)

    elements.append(Spacer(1, 12))  # Adiciona um pequeno espaço antes das notas

    nota_final = Paragraph(f"Nota Final: {resultado.pesototal:.2f}", bold_style)
    elements.append(nota_final)

    # Determinar a menor nota
    menor_nota = min(nota_meta, nota_plano, nota_acao)
    if menor_nota == nota_meta:
        mensagem = "A sua pontuação em Gestão de Custos indica que a etapa de Meta requer mais atenção. Para A avançar, concentre-se em otimizar os Estudos de Viabilidade, garantindo o alinhamento entre a expectativa de custo total, a tipologia do produto e o VGV. No Orçamento Paramétrico, é importante validar o produto, o padrão do empreendimento e as particularidades técnicas. Já no Orçamento Pré-Executivo e Planejamento Inicial, assegure que todos os parâmetros estejam bem estabelecidos para definição da meta de custo total e lançamento comercial."
    elif menor_nota == nota_plano:
        mensagem = "A sua pontuação em Gestão de Custos indica que a etapa de Plano requer mais atenção. Para melhorar nesta fase, é fundamental aprimorar a elaboração do Orçamento Operacional. Para isso, concentre-se na correta segmentação da Estrutura Analítica de Projeto (EAP), na validação detalhada das composições de serviço e na prospecção de propostas comerciais para itens da Curva A. Quanto ao Planejamento Operacional, foque na definição dos critérios de medição para as atividades do cronograma, além de elaborar um planejamento de compras e contratações adequado. "
    else:
        mensagem = "A sua pontuação em Gestão de Custos indica que a etapa de Ação precisa de atenção. Para avançar nesta etapa, é crucial concentrar-se no Monitoramento e Controle durante a execução da obra. Garanta que as equipes de Suprimentos, Execução e Financeiro estejam devidamente treinadas e engajadas no uso das ferramentas e na inserção das informações necessárias. Além disso, é importante gerenciar ativamente os contratos e medições para assegurar que todos os aspectos do projeto estejam sendo acompanhados de perto e ajustados conforme necessário, a partir de indicadores de custo e prazo atualizados."

    mensagem_final = Paragraph(mensagem, default_style)
    elements.append(mensagem_final)

    doc.build(elements)
    buffer.seek(0)

    # Verificar o consentimento antes de enviar o e-mail
    destinatarios = []
    if cliente.consent:
        destinatarios.append(cliente.email)

    destinatarios.append('cliente@taticosolucoes.com.br')  # E-mail fixo adicional

    if destinatarios:
        msg = Message("Resultado do Diagnóstico de Eficiência", recipients=destinatarios)
        msg.body = "Segue em anexo o resultado do Diagnóstico de Eficiência em Gestão de Custos da sua empresa."
        msg.attach(nome_arquivo_pdf, "application/pdf", buffer.getvalue())

        try:
            mail.send(msg)
        except Exception as e:
            flash(f"Erro ao enviar o e-mail: {str(e)}", "danger")

    # Oferecer o download do PDF diretamente
    return send_file(buffer, download_name=nome_arquivo_pdf, as_attachment=True)
