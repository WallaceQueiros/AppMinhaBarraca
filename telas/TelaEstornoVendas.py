from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QVBoxLayout,
    QHBoxLayout, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from datetime import datetime
from db import conectar


class TelaEstornoVendas(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.itens_estorno = []
        self.total_estorno = 0.0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        titulo = QLabel("Estorno de Vendas")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.entry_codigo = QLineEdit()
        self.entry_codigo.setPlaceholderText("Código do Produto")
        layout.addWidget(self.entry_codigo)

        btn_adicionar = QPushButton("Adicionar ao Estorno")
        btn_adicionar.clicked.connect(self.adicionar_item_estorno)
        layout.addWidget(btn_adicionar)

        self.lista_estorno = QListWidget()
        layout.addWidget(self.lista_estorno)

        btn_remover = QPushButton("Remover Item Selecionado")
        btn_remover.clicked.connect(self.remover_item)
        layout.addWidget(btn_remover)

        self.label_total_estorno = QLabel("Total Estornado: R$ 0.00")
        self.label_total_estorno.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.label_total_estorno)

        self.check_furo = QCheckBox("Permitir furo de estoque")
        layout.addWidget(self.check_furo)

        botoes = QHBoxLayout()

        btn_confirmar = QPushButton("Confirmar Estorno")
        btn_confirmar.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        btn_confirmar.clicked.connect(self.confirmar_estorno)
        botoes.addWidget(btn_confirmar)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaVendas"))
        botoes.addWidget(btn_voltar)

        layout.addLayout(botoes)
        self.setLayout(layout)

    def adicionar_item_estorno(self):
        if len(self.itens_estorno) >= 10:
            QMessageBox.warning(self, "Limite", "Limite de 10 itens por estorno atingido.")
            return

        codigo = self.entry_codigo.text().strip()
        if not codigo:
            QMessageBox.warning(self, "Erro", "Digite o código do produto.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT descricao, valor_venda FROM produtos WHERE codigo = ?", (codigo,))
            produto = cursor.fetchone()
            conn.close()

            if not produto:
                QMessageBox.warning(self, "Erro", "Produto não encontrado.")
                return

            descricao, valor = produto
            self.itens_estorno.append((codigo, descricao, valor))
            self.total_estorno += valor
            self.lista_estorno.addItem(f"{descricao} - R$ {valor:.2f}")
            self.label_total_estorno.setText(f"Total Estornado: R$ {self.total_estorno:.2f}")
            self.entry_codigo.clear()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar item:\n{e}")

    def remover_item(self):
        idx = self.lista_estorno.currentRow()
        if idx >= 0:
            _, _, valor = self.itens_estorno.pop(idx)
            self.total_estorno -= valor
            self.lista_estorno.takeItem(idx)
            self.label_total_estorno.setText(f"Total Estornado: R$ {self.total_estorno:.2f}")
        else:
            QMessageBox.warning(self, "Atenção", "Selecione um item para remover.")

    def confirmar_estorno(self):
        if not self.itens_estorno:
            QMessageBox.warning(self, "Atenção", "Nenhum item para estornar.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for codigo, descricao, valor in self.itens_estorno:
                cursor.execute("SELECT id, adicional, vendido, estoque_atual FROM estoque WHERE codigo_produto = ?",
                               (codigo,))
                estoque = cursor.fetchone()

                if estoque:
                    est_id, adicional, vendido, estoque_atual = estoque
                    if self.check_furo.isChecked():
                        cursor.execute("""
                            UPDATE estoque 
                            SET estoque_atual = 0 
                            WHERE id = ?
                        """, (est_id,))
                    else:
                        cursor.execute("UPDATE estoque SET adicional = ?, estoque_atual = ? WHERE id = ?",
                                       (adicional + 1, estoque_atual + 1, est_id))
                elif self.check_furo.isChecked():
                    cursor.execute("""
                        INSERT INTO estoque (codigo_produto, estoque_inicial, adicional, vendido, estoque_atual)
                        VALUES (?, 0, 0, 0, 0)
                    """, (codigo,))
                else:
                    QMessageBox.critical(self, "Erro", f"Produto {codigo} sem estoque. Ative o furo de estoque.")
                    conn.rollback()
                    return

                nome = self.controller.usuario_logado or "ESTORNO"
                cpf = self.controller.cpf_logado or "00000000000"

                cursor.execute("""
                    INSERT INTO vendas (nome_cliente, cpf_cliente, produto, valor, forma_pagamento, data_venda)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (nome, cpf, descricao, -valor, "ESTORNADO", data))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sucesso", f"Estorno realizado!\nTotal: R$ {self.total_estorno:.2f}")
            self.limpar_estorno()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao confirmar estorno:\n{e}")

    def limpar_estorno(self):
        self.itens_estorno.clear()
        self.total_estorno = 0.0
        self.lista_estorno.clear()
        self.label_total_estorno.setText("Total Estornado: R$ 0.00")
        self.entry_codigo.clear()
        self.check_furo.setChecked(False)
