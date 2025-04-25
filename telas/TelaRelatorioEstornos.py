from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt
from db import conectar


class TelaRelatorioEstornos(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        titulo = QLabel("Relatório de Estornos")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels([
            "Usuário", "CPF", "Produto", "Valor Estornado", "Data"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela)

        btn_recarregar = QPushButton("Recarregar")
        btn_recarregar.clicked.connect(self.carregar_estornos)
        layout.addWidget(btn_recarregar)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaAdminMenu"))
        layout.addWidget(btn_voltar)

        self.setLayout(layout)
        self.carregar_estornos()

    def carregar_estornos(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nome_cliente, cpf_cliente, produto, valor, data_venda
                FROM vendas
                WHERE forma_pagamento = 'ESTORNADO'
                ORDER BY data_venda DESC
            """)
            estornos = cursor.fetchall()
            conn.close()

            self.tabela.setRowCount(0)
            for row_idx, (nome, cpf, produto, valor, data) in enumerate(estornos):
                self.tabela.insertRow(row_idx)
                self.tabela.setItem(row_idx, 0, QTableWidgetItem(nome))
                self.tabela.setItem(row_idx, 1, QTableWidgetItem(cpf))
                self.tabela.setItem(row_idx, 2, QTableWidgetItem(produto))
                self.tabela.setItem(row_idx, 3, QTableWidgetItem(f"R$ {abs(valor):.2f}"))
                self.tabela.setItem(row_idx, 4, QTableWidgetItem(data))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar estornos:\n{e}")
