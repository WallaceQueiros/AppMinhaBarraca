from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
)
from db import conectar

class TelaCadastroProduto(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout_principal = QVBoxLayout()

        titulo = QLabel("Cadastro de Produto")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout_principal.addWidget(titulo)

        form_layout = QFormLayout()

        self.entry_codigo = QLineEdit()
        self.entry_codigo.setReadOnly(True)  # código será gerado automaticamente
        form_layout.addRow("Código do Produto:", self.entry_codigo)

        self.entry_descricao = QLineEdit()
        form_layout.addRow("Descrição:", self.entry_descricao)

        self.entry_valor_venda = QLineEdit()
        form_layout.addRow("Valor de Venda (R$):", self.entry_valor_venda)

        self.entry_valor_custo = QLineEdit()
        form_layout.addRow("Valor de Custo (R$):", self.entry_valor_custo)

        self.entry_estoque_inicial = QLineEdit()
        self.entry_estoque_inicial.setPlaceholderText("Opcional")
        form_layout.addRow("Estoque Inicial:", self.entry_estoque_inicial)

        layout_principal.addLayout(form_layout)

        btn_cadastrar = QPushButton("Cadastrar")
        btn_cadastrar.clicked.connect(self.cadastrar_produto)
        layout_principal.addWidget(btn_cadastrar)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaAdminMenu"))
        layout_principal.addWidget(btn_voltar)

        self.setLayout(layout_principal)
        self.gerar_codigo_automatico()

    def gerar_codigo_automatico(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(CAST(codigo AS INTEGER)) FROM produtos")
            ultimo_codigo = cursor.fetchone()[0]
            proximo_codigo = str((int(ultimo_codigo) + 1) if ultimo_codigo else 1)
            self.entry_codigo.setText(proximo_codigo)
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar código do produto:\n{e}")

    def cadastrar_produto(self):
        codigo = self.entry_codigo.text().strip()
        descricao = self.entry_descricao.text().strip()
        valor_venda = self.entry_valor_venda.text().strip().replace(",", ".")
        valor_custo = self.entry_valor_custo.text().strip().replace(",", ".")
        estoque_inicial = self.entry_estoque_inicial.text().strip()

        if not descricao or not valor_venda or not valor_custo:
            QMessageBox.warning(self, "Erro", "Todos os campos devem ser preenchidos.")
            return

        try:
            valor_venda = float(valor_venda)
            valor_custo = float(valor_custo)
            if valor_venda <= 0 or valor_custo <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valores inválidos. Verifique os campos numéricos.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO produtos (codigo, descricao, valor_venda, valor_custo)
                VALUES (?, ?, ?, ?)
            """, (codigo, descricao, valor_venda, valor_custo))

            cursor.execute("""
                INSERT INTO estoque (codigo_produto, estoque_inicial, adicional, vendido, estoque_atual)
                VALUES (?, ?, 0, 0, ?)
            """, (codigo, estoque_inicial, estoque_inicial))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sucesso", "Produto cadastrado com sucesso!")
            self.entry_descricao.clear()
            self.entry_valor_venda.clear()
            self.entry_valor_custo.clear()
            self.entry_estoque_inicial.clear()
            self.gerar_codigo_automatico()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao cadastrar produto:\n{e}")
