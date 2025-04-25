from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox
)

from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtCore import Qt
from db import conectar


class TelaVisualizarEstoque(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        titulo = QLabel("Estoque Atual")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Produto", "Estoque Inicial", "Adicionado", "Disponível", "Status"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.tabela)

        # Botões
        btn_recarregar = QPushButton("Recarregar")
        btn_recarregar.clicked.connect(self.carregar_estoque)
        layout.addWidget(btn_recarregar)

        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaAdminMenu"))
        layout.addWidget(btn_voltar)

        self.setLayout(layout)
        self.carregar_estoque()

    def carregar_estoque(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.codigo_produto, p.descricao, e.estoque_inicial, e.adicional, e.estoque_atual
                FROM estoque e
                JOIN produtos p ON e.codigo_produto = p.codigo
                ORDER BY CAST(e.codigo_produto AS INTEGER) ASC
            """)
            dados = cursor.fetchall()
            conn.close()

            self.tabela.setRowCount(0)

            for row_idx, (codigo, descricao, inicial, adicional, atual) in enumerate(dados):
                inicial = int(inicial) if inicial else 0
                adicional = int(adicional) if adicional else 0
                atual = int(atual) if atual else 0
                status = "✅ Disponível" if atual > 0 else "❌ Finalizado"

                self.tabela.insertRow(row_idx)
                self.tabela.setItem(row_idx, 0, QTableWidgetItem(codigo))
                self.tabela.setItem(row_idx, 1, QTableWidgetItem(descricao))
                self.tabela.setItem(row_idx, 2, QTableWidgetItem(str(inicial)))
                self.tabela.setItem(row_idx, 3, QTableWidgetItem(str(adicional)))
                self.tabela.setItem(row_idx, 4, QTableWidgetItem(str(atual)))
                self.tabela.setItem(row_idx, 5, QTableWidgetItem(status))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar estoque:\n{e}")
