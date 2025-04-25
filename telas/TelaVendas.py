from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QListWidget, QMessageBox, QComboBox, QDialog, QTableWidget,
    QTableWidgetItem
)
from PyQt6.QtCore import Qt
from datetime import datetime
from db import conectar
from ficha import gerar_fichas_pdf


class TelaVendas(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.itens = []
        self.total = 0.0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        titulo = QLabel("Finalização de Venda")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.entry_codigo = QLineEdit()
        self.entry_codigo.setPlaceholderText("Código do Produto")
        layout.addWidget(self.entry_codigo)

        btn_adicionar = QPushButton("Adicionar Produto")
        btn_adicionar.clicked.connect(self.adicionar_produto)
        layout.addWidget(btn_adicionar)

        self.lista_itens = QListWidget()
        layout.addWidget(self.lista_itens)

        btn_remover = QPushButton("Remover Item Selecionado")
        btn_remover.clicked.connect(self.remover_item)
        layout.addWidget(btn_remover)

        self.label_total = QLabel("Total: R$ 0.00")
        self.label_total.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.label_total)

        self.forma_pagamento = QComboBox()
        self.forma_pagamento.addItems(["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito", "Fiado", "Cortesia"])
        self.forma_pagamento.currentTextChanged.connect(self.atualizar_campos_forma_pagamento)
        layout.addWidget(self.forma_pagamento)

        self.entry_recebido = QLineEdit()
        self.entry_recebido.setPlaceholderText("Valor Recebido (R$)")
        layout.addWidget(self.entry_recebido)

        self.entry_nome_fiado = QLineEdit()
        self.entry_nome_fiado.setPlaceholderText("Nome do cliente")
        self.entry_nome_fiado.hide()
        layout.addWidget(self.entry_nome_fiado)

        botoes = QHBoxLayout()

        btn_finalizar = QPushButton("Finalizar Venda")
        btn_finalizar.clicked.connect(self.finalizar_venda)
        botoes.addWidget(btn_finalizar)

        btn_cancelar = QPushButton("Cancelar Venda Toda")
        btn_cancelar.clicked.connect(self.limpar_venda)
        botoes.addWidget(btn_cancelar)

        layout.addLayout(botoes)

        btn_estoque = QPushButton("Visualizar Estoque")
        btn_estoque.clicked.connect(self.visualizar_estoque)
        layout.addWidget(btn_estoque)

        btn_estornar = QPushButton("Estornar Venda")
        btn_estornar.setStyleSheet("background-color: orange; color: black; font-weight: bold;")
        btn_estornar.clicked.connect(lambda: self.controller.trocar_tela("TelaEstornoVendas"))
        layout.addWidget(btn_estornar)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaLogin"))
        layout.addWidget(btn_voltar)

        self.setLayout(layout)
        self.atualizar_campos_forma_pagamento()

    def atualizar_campos_forma_pagamento(self):
        forma = self.forma_pagamento.currentText()
        self.entry_recebido.setVisible(forma == "Dinheiro")
        self.entry_nome_fiado.setVisible(forma in ["Fiado", "Cortesia"])

    def adicionar_produto(self):
        codigo = self.entry_codigo.text().strip()
        if not codigo:
            QMessageBox.warning(self, "Erro", "Digite o código do produto.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT descricao, valor_venda FROM produtos WHERE codigo = ?", (codigo,))
            produto = cursor.fetchone()

            if not produto:
                QMessageBox.warning(self, "Erro", "Produto não encontrado.")
                conn.close()
                return

            # Verifica estoque atual disponível
            cursor.execute("SELECT estoque_atual FROM estoque WHERE codigo_produto = ?", (codigo,))
            estoque = cursor.fetchone()
            conn.close()

            if not estoque:
                QMessageBox.warning(self, "Estoque Indisponível", "Este produto ainda não possui estoque registrado.")
                return

            disponivel = estoque[0]
            if disponivel <= 0:
                QMessageBox.warning(self, "Estoque Insuficiente", "Produto sem estoque disponível.")
                return

            descricao, valor = produto
            self.itens.append((codigo, descricao, valor))
            self.total += valor
            self.lista_itens.addItem(f"{descricao} - R$ {valor:.2f}")
            self.label_total.setText(f"Total: R$ {self.total:.2f}")
            self.entry_codigo.clear()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar produto:\n{e}")

    def remover_item(self):
        idx = self.lista_itens.currentRow()
        if idx >= 0:
            _, _, valor = self.itens.pop(idx)
            self.total -= valor
            self.lista_itens.takeItem(idx)
            self.label_total.setText(f"Total: R$ {self.total:.2f}")
        else:
            QMessageBox.warning(self, "Atenção", "Selecione um item para remover.")

    def finalizar_venda(self):
        if not self.itens:
            QMessageBox.warning(self, "Atenção", "Nenhum produto adicionado.")
            return

        forma = self.forma_pagamento.currentText()
        recebido = self.entry_recebido.text().strip().replace(",", ".")
        nome_cliente = self.entry_nome_fiado.text().strip() if forma in ["Fiado", "Cortesia"] else (self.controller.usuario_logado or "Cliente")
        cpf_cliente = self.controller.cpf_logado or "00000000000"

        try:
            recebido_valor = float(recebido) if forma == "Dinheiro" and recebido else 0.0
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valor recebido inválido.")
            return

        if forma == "Dinheiro" and recebido_valor < self.total:
            QMessageBox.warning(self, "Erro", "Valor recebido menor que o total.")
            return

        troco = recebido_valor - self.total if forma == "Dinheiro" else 0.0

        try:
            conn = conectar()
            cursor = conn.cursor()
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for codigo, descricao, valor in self.itens:
                cursor.execute("""
                    INSERT INTO vendas (nome_cliente, cpf_cliente, produto, valor, forma_pagamento, data_venda)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (nome_cliente, cpf_cliente, descricao, valor, forma, data))

                cursor.execute("SELECT id, estoque_atual, vendido FROM estoque WHERE codigo_produto = ?", (codigo,))
                estoque = cursor.fetchone()
                if estoque:
                    est_id, atual, vendido = estoque
                    novo_atual = atual - 1
                    cursor.execute("UPDATE estoque SET vendido = ?, estoque_atual = ? WHERE id = ?", (vendido + 1, novo_atual, est_id))

            conn.commit()
            conn.close()

            msg = f"Venda finalizada com sucesso!\nTotal: R$ {self.total:.2f}"
            if forma == "Dinheiro":
                msg += f"\nTroco: R$ {troco:.2f}"
            QMessageBox.information(self, "Sucesso", msg)

            # Gerar fichas
            nomes_produtos = [item[1] for item in self.itens]
            caminho = gerar_fichas_pdf(nomes_produtos)
            QMessageBox.information(self, "Fichas", f"Fichas geradas com sucesso em:\n{caminho}")

            self.limpar_venda()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao registrar venda:\n{e}")

    def visualizar_estoque(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Estoque Atual")
        dialog.setMinimumSize(400, 300)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Código", "Produto", "Disponível"])

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.codigo_produto, p.descricao, e.estoque_atual
                FROM estoque e
                JOIN produtos p ON e.codigo_produto = p.codigo
                ORDER BY CAST(e.codigo_produto AS INTEGER) ASC
            """)
            dados = cursor.fetchall()
            conn.close()

            table.setRowCount(len(dados))
            for i, (codigo, nome, disponivel) in enumerate(dados):
                table.setItem(i, 0, QTableWidgetItem(str(codigo)))
                table.setItem(i, 1, QTableWidgetItem(nome))
                table.setItem(i, 2, QTableWidgetItem(str(disponivel)))
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar estoque:\n{e}")
            return

        layout = QVBoxLayout()
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec()

    def limpar_venda(self):
        self.itens.clear()
        self.total = 0.0
        self.lista_itens.clear()
        self.label_total.setText("Total: R$ 0.00")
        self.entry_codigo.clear()
        self.entry_recebido.clear()
        self.entry_nome_fiado.clear()
