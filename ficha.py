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

        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)

        for idx, produto in enumerate(sorted(lista_produtos, key=lambda x: x.lower()), start=1):
            # Cria imagem
            img = Image.new("RGB", (576, 800), "white")
            draw = ImageDraw.Draw(img)

            font_paroquia = ImageFont.truetype(str(caminho_fontes / "LuckiestGuy-Regular.ttf"), 32)
            font_barraca = ImageFont.truetype(str(caminho_fontes / "LuckiestGuy-Regular.ttf"), 32)
            font_festa = ImageFont.truetype(str(caminho_fontes / "PermanentMarker-Regular.ttf"), 28)
            font_produto = ImageFont.truetype(str(caminho_fontes / "DMSerifText-Regular.ttf"), 36)
            font_info = ImageFont.truetype(str(caminho_fontes / "TitanOne-Regular.ttf"), 20)

            y = 30
            draw.text((50, y), "Paróquia Santa Teresinha", font=font_paroquia, fill="black")
            y += 40
            draw.text((50, y), "de Santanésia", font=font_barraca, fill="black")
            y += 60
            draw.text((50, y), "Cinema - Com N. Sra.de.Fátima", font=font_festa, fill="black")
            y += 60
            produto_texto = produto
            if texto_extra:
                produto_texto += f" ({texto_extra})"
            draw.text((50, y), produto_texto, font=font_produto, fill="black")
            y += 80
            draw.text((50, y), f"Validade: {validade}", font=font_info, fill="black")
            y += 30
            draw.text((50, y), f"Ficha: {idx}/{total}", font=font_info, fill="black")

            # Agora imprime a imagem diretamente
            pdc.StartDoc(f"Ficha {idx}")
            pdc.StartPage()

            dib = ImageWin.Dib(img)
            dib.draw(pdc.GetHandleOutput(), (0, 0, 576, 800))

            pdc.EndPage()
            pdc.EndDoc()

        pdc.DeleteDC()
        print("✅ Fichas enviadas para impressão!")

    except Exception as e:
        print(f"❌ Erro ao imprimir fichas: {e}")
