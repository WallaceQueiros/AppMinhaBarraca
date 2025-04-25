from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox,
    QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from db import conectar


class TelaEstoque(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        titulo = QLabel("Controle de Estoque")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.produto_dropdown = QComboBox()
        layout.addWidget(QLabel("Selecione um Produto:"))
        layout.addWidget(self.produto_dropdown)

        self.entry_quantidade = QLineEdit()
        self.entry_quantidade.setPlaceholderText("Quantidade a adicionar")
        layout.addWidget(self.entry_quantidade)

        btn_adicionar = QPushButton("Adicionar ao Estoque")
        btn_adicionar.clicked.connect(self.adicionar_estoque)
        layout.addWidget(btn_adicionar)

        btn_zerar = QPushButton("Zerar Estoque do Produto Selecionado")
        btn_zerar.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        btn_zerar.clicked.connect(self.zerar_estoque)
        layout.addWidget(btn_zerar)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaAdminMenu"))
        layout.addWidget(btn_voltar)

        self.setLayout(layout)
        self.carregar_produtos()

    def showEvent(self, event):
        super().showEvent(event)
        self.carregar_produtos()

    def carregar_produtos(self):
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

    def adicionar_estoque(self):
        produto_info = self.produto_dropdown.currentText()
        qtd_texto = self.entry_quantidade.text().strip()

        if not produto_info or not qtd_texto:
            QMessageBox.warning(self, "Erro", "Selecione um produto e informe a quantidade.")
            return

        try:
            qtd = int(qtd_texto)
            if qtd <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erro", "A quantidade deve ser um número inteiro positivo.")
            return

        codigo = produto_info.split(" - ")[0] if " - " in produto_info else produto_info

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT id, adicional, estoque_atual FROM estoque WHERE codigo_produto = ?", (codigo,))
            registro = cursor.fetchone()

            if registro:
                est_id, adicional, atual = registro
                adicional = int(adicional or 0)  # <- protege contra None ou vazio
                atual = int(atual or 0)  # <- protege contra None ou vazio
                novo_adicional = adicional + qtd
                novo_atual = atual + qtd
                cursor.execute(
                    "UPDATE estoque SET adicional = ?, estoque_atual = ? WHERE id = ?",
                    (novo_adicional, novo_atual, est_id)
                )
            else:
                cursor.execute("""
                    INSERT INTO estoque (codigo_produto, estoque_inicial, adicional, vendido, estoque_atual)
                    VALUES (?, 0, ?, 0, ?)
                """, (codigo, qtd, qtd))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sucesso", "Estoque atualizado com sucesso!")
            self.entry_quantidade.clear()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar estoque:\n{e}")

    def zerar_estoque(self):
        produto_info = self.produto_dropdown.currentText()
        if not produto_info:
            QMessageBox.warning(self, "Erro", "Selecione um produto para zerar o estoque.")
            return

        codigo = produto_info.split(" - ")[0] if " - " in produto_info else produto_info

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM estoque WHERE codigo_produto = ?", (codigo,))
            resultado = cursor.fetchone()

            if resultado:
                cursor.execute("""
                    UPDATE estoque 
                    SET estoque_atual = 0 
                    WHERE codigo_produto = ?
                """, (codigo,))
                conn.commit()
                QMessageBox.information(self, "Sucesso", "Estoque do produto foi zerado com sucesso!")
            else:
                QMessageBox.warning(self, "Aviso", "Este produto ainda não possui registro de estoque.")

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao zerar estoque:\n{e}")
