import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def gerar_fichas_pdf(lista_produtos):
    produtos = sorted(lista_produtos, key=lambda x: x.lower())
    total = len(produtos)
    validade = datetime.now().strftime("%d/%m/%Y")

    pasta = "fichas"
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f"ficha_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    caminho_saida = os.path.join(pasta, nome_arquivo)

    c = canvas.Canvas(caminho_saida, pagesize=A4)
    largura, altura = A4
    y = altura - 100

    # Carregar o ícone
    caminho_icone = "icone_festa.png"  # Coloque sua imagem nessa pasta
    if os.path.exists(caminho_icone):
        icone = ImageReader(caminho_icone)
    else:
        icone = None

    for i, nome in enumerate(produtos, start=1):
        if y < 150:
            c.showPage()
            y = altura - 100

        # Ícone no topo
        if icone:
            c.drawImage(icone, largura/2 - 25, y, width=50, height=50, preserveAspectRatio=True, mask='auto')
            y -= 60  # Ajusta espaço depois da imagem

        # Título da paróquia e barraca
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(largura / 2, y, "Paróquia Santa Teresinha de Santanésia")
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(largura / 2, y - 20, "Festa do Trabalhador 🎉")

        # Produto
        c.setFont("Helvetica", 18)
        c.drawCentredString(largura / 2, y - 50, f"Produto: {nome}")

        # Validade e número da ficha
        c.setFont("Helvetica", 10)
        c.drawCentredString(largura / 2, y - 75, f"Validade: {validade}")
        c.drawCentredString(largura / 2, y - 88, f"Ficha: {i}/{total}")

        # Separador (opcional, sem borda geral)
        c.setFont("Helvetica", 9)
        c.drawCentredString(largura / 2, y - 102, "-" * 36)

        # Espaço para próxima ficha
        y -= 150

    c.save()
    return caminho_saida
