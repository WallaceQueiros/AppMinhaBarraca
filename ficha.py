import os
from datetime import datetime
from pathlib import Path
import win32con
import win32ui
import win32print
from PIL import Image, ImageDraw, ImageFont, ImageWin

def imprimir_fichas_thermal(lista_produtos, texto_extra=None):
    printer_name = "ELGIN i9(USB)"  # Nome da impressora no Windows

    try:
        caminho_fontes = Path(__file__).parent / "fonts"
        validade = datetime.now().strftime("%d/%m/%Y")
        total = len(lista_produtos)

        largura_imagem = 576
        altura_imagem = 800

        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)

        for idx, produto in enumerate(sorted(lista_produtos, key=lambda x: x.lower()), start=1):
            img = Image.new("RGB", (largura_imagem, altura_imagem), "white")
            draw = ImageDraw.Draw(img)

            font_paroquia = ImageFont.truetype(str(caminho_fontes / "LuckiestGuy-Regular.ttf"), 32)
            font_barraca = ImageFont.truetype(str(caminho_fontes / "LuckiestGuy-Regular.ttf"), 32)
            font_festa = ImageFont.truetype(str(caminho_fontes / "LuckiestGuy-Regular.ttf"), 26)
            font_produto = ImageFont.truetype(str(caminho_fontes / "DMSerifText-Regular.ttf"), 36)
            font_info = ImageFont.truetype(str(caminho_fontes / "DMSerifText-Regular.ttf"), 18)

            y = 30

            def desenhar_texto_centralizado(texto, fonte, y_pos, cor="black"):
                largura_texto = draw.textlength(texto, font=fonte)
                x = (largura_imagem - largura_texto) / 2
                draw.text((x, y_pos), texto, font=fonte, fill=cor)

            desenhar_texto_centralizado("Paróquia Santa Teresinha", font_paroquia, y)
            y += 40
            desenhar_texto_centralizado("de Santanésia", font_barraca, y)
            y += 60
            desenhar_texto_centralizado("Cinema - Com N. Sra. de. Fátima", font_festa, y)
            y += 60

            produto_texto = produto
            if texto_extra:
                produto_texto += f" ({texto_extra})"
            desenhar_texto_centralizado(produto_texto, font_produto, y)
            y += 80

            desenhar_texto_centralizado(f"{validade}", font_info, y)
            y += 30
            desenhar_texto_centralizado(f"{idx}/{total}", font_info, y)

            bmp_path = Path(__file__).parent / "ficha_temp.bmp"
            img.save(bmp_path)

            # Impressão
            pdc.StartDoc(f"Ficha {idx}")
            pdc.StartPage()

            dib = ImageWin.Dib(img)
            dib.draw(pdc.GetHandleOutput(), (0, 0, largura_imagem, altura_imagem))

            pdc.EndPage()
            pdc.EndDoc()

        pdc.DeleteDC()
        print("✅ Fichas enviadas para impressão!")

    except Exception as e:
        print(f"❌ Erro ao imprimir fichas: {e}")
