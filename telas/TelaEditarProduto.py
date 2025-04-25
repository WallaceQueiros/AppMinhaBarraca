from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QComboBox, QLineEdit,
    QPushButton, QMessageBox
)
from db import conectar


class TelaEditarProduto(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        titulo = QLabel("Editar Produto")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        layout.addWidget(QLabel("Selecione o Produto:"))
        self.produto_dropdown = QComboBox()
        layout.addWidget(self.produto_dropdown)

        self.entry_descricao = QLineEdit()
        self.entry_descricao.setPlaceholderText("Descrição")
        layout.addWidget(self.entry_descricao)

        self.entry_valor_venda = QLineEdit()
        self.entry_valor_venda.setPlaceholderText("Valor de Venda (R$)")
        layout.addWidget(self.entry_valor_venda)

        self.entry_valor_custo = QLineEdit()
        self.entry_valor_custo.setPlaceholderText("Valor de Custo (R$)")
        layout.addWidget(self.entry_valor_custo)

        btn_carregar = QPushButton("Carregar Produto")
        btn_carregar.clicked.connect(self.carregar_produto)
        layout.addWidget(btn_carregar)

        btn_salvar = QPushButton("Salvar Alterações")
        btn_salvar.clicked.connect(self.salvar_alteracoes)
        layout.addWidget(btn_salvar)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaAdminMenu"))
        layout.addWidget(btn_voltar)

        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)
        self.atualizar_produtos()

    def atualizar_produtos(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, descricao FROM produtos ORDER BY CAST(codigo AS INTEGER)")
            produtos = cursor.fetchall()
            conn.close()

            self.produto_dropdown.clear()
            for codigo, descricao in produtos:
                self.produto_dropdown.addItem(f"{codigo} - {descricao}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produtos:\n{e}")

    def carregar_produto(self):
        codigo = self._get_codigo_selecionado()
        if not codigo:
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT descricao, valor_venda, valor_custo FROM produtos WHERE codigo = ?", (codigo,))
            produto = cursor.fetchone()
            conn.close()

            if produto:
                descricao, venda, custo = produto
                self.entry_descricao.setText(descricao)
                self.entry_valor_venda.setText(str(venda).replace('.', ','))
                self.entry_valor_custo.setText(str(custo).replace('.', ','))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produto:\n{e}")

    def salvar_alteracoes(self):
        codigo = self._get_codigo_selecionado()
        if not codigo:
            return

        descricao = self.entry_descricao.text().strip()
        valor_venda = self.entry_valor_venda.text().strip().replace(',', '.')
        valor_custo = self.entry_valor_custo.text().strip().replace(',', '.')

        if not descricao or not valor_venda or not valor_custo:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        try:
            valor_venda = float(valor_venda)
            valor_custo = float(valor_custo)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valores devem ser numéricos.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE produtos
                SET descricao = ?, valor_venda = ?, valor_custo = ?
                WHERE codigo = ?
            """, (descricao, valor_venda, valor_custo, codigo))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sucesso", "Produto atualizado com sucesso!")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar alterações:\n{e}")

    def _get_codigo_selecionado(self):
        texto = self.produto_dropdown.currentText()
        if not texto:
            QMessageBox.warning(self, "Erro", "Nenhum produto selecionado.")
            return None
        return texto.split(" - ")[0]
