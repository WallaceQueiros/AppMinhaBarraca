from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox, QHeaderView
)
from PyQt6.QtCore import Qt
from db import conectar


class TelaRelatorioVendas(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(30, 30, 30, 30)
        layout_principal.setSpacing(20)

        titulo = QLabel("Relatório de Vendas")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(titulo)

        layout_secoes = QHBoxLayout()
        layout_secoes.setSpacing(20)

        # --- Produtos em Quantidade ---
        grupo_qtd = QGroupBox("Produtos (Quantidade)")
        layout_qtd = QVBoxLayout()
        self.label_total_qtd = QLabel("Total Vendidos: 0 itens")
        self.label_total_qtd.setStyleSheet("color: blue; font-weight: bold;")
        layout_qtd.addWidget(self.label_total_qtd, alignment=Qt.AlignmentFlag.AlignCenter)

        self.tabela_qtd = QTableWidget()
        self.tabela_qtd.setColumnCount(3)
        self.tabela_qtd.setHorizontalHeaderLabels(["Produto", "Vendidos", "Cortesia"])
        self.tabela_qtd.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_qtd.verticalHeader().setVisible(False)
        layout_qtd.addWidget(self.tabela_qtd)
        grupo_qtd.setLayout(layout_qtd)

        # --- Produtos em Valor ---
        grupo_valor = QGroupBox("Produtos (Valor)")
        layout_valor = QVBoxLayout()
        self.label_total_valor = QLabel("Total Pago: R$ 0,00")
        self.label_total_valor.setStyleSheet("color: green; font-weight: bold;")
        layout_valor.addWidget(self.label_total_valor, alignment=Qt.AlignmentFlag.AlignCenter)

        self.tabela_valor = QTableWidget()
        self.tabela_valor.setColumnCount(2)
        self.tabela_valor.setHorizontalHeaderLabels(["Produto", "Valor R$"])
        self.tabela_valor.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_valor.verticalHeader().setVisible(False)
        layout_valor.addWidget(self.tabela_valor)
        grupo_valor.setLayout(layout_valor)

        layout_secoes.addWidget(grupo_qtd)
        layout_secoes.addWidget(grupo_valor)
        layout_principal.addLayout(layout_secoes)

        # --- Formas de Pagamento ---
        grupo_formas = QGroupBox("Formas de Pagamento")
        layout_formas = QVBoxLayout()
        self.tabela_formas = QTableWidget()
        self.tabela_formas.setColumnCount(3)
        self.tabela_formas.setHorizontalHeaderLabels(["Forma", "Total R$", "Qtd."])
        self.tabela_formas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_formas.verticalHeader().setVisible(False)
        layout_formas.addWidget(self.tabela_formas)
        grupo_formas.setLayout(layout_formas)
        layout_principal.addWidget(grupo_formas)

        # --- Fiado/Cortesia por Cliente ---
        grupo_fiado = QGroupBox("Fiado e Cortesia por Cliente")
        layout_fiado = QVBoxLayout()
        self.tabela_fiado = QTableWidget()
        self.tabela_fiado.setColumnCount(3)
        self.tabela_fiado.setHorizontalHeaderLabels(["Nome", "Forma de Pagamento", "Valor Total R$"])
        self.tabela_fiado.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_fiado.verticalHeader().setVisible(False)
        layout_fiado.addWidget(self.tabela_fiado)
        grupo_fiado.setLayout(layout_fiado)
        layout_principal.addWidget(grupo_fiado)

        # Botão Voltar
        btn_voltar = QPushButton("Voltar ao Menu")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaAdminMenu"))
        layout_principal.addWidget(btn_voltar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout_principal)

    def showEvent(self, event):
        super().showEvent(event)
        self.carregar_dados()

    def carregar_dados(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nome_cliente, produto, valor, forma_pagamento, data_venda
                FROM vendas
                WHERE forma_pagamento != 'ESTORNADO'
            """)
            vendas = cursor.fetchall()
            conn.close()

            vendidos = {}
            cortesia = {}
            produtos_valor = {}
            formas_valor = {}
            formas_transacoes = {}
            fiado_cortesia = {}

            total_itens_vendidos = 0
            total_valor_pago = 0.0
            transacoes_contadas = set()

            for nome, produto, valor, forma, data in vendas:
                # Contagem de quantidade
                if forma.upper() == "CORTESIA":
                    cortesia[produto] = cortesia.get(produto, 0) + 1
                else:
                    vendidos[produto] = vendidos.get(produto, 0) + 1
                    total_itens_vendidos += 1

                # Valor dos produtos
                if forma.upper() not in ["FIADO", "CORTESIA"]:
                    produtos_valor[produto] = produtos_valor.get(produto, 0.0) + valor
                    total_valor_pago += valor

                # Formas de pagamento
                formas_valor[forma] = formas_valor.get(forma, 0.0) + valor
                transacao_id = f"{nome}-{forma}-{data.split()[0]}"
                if transacao_id not in transacoes_contadas:
                    transacoes_contadas.add(transacao_id)
                    formas_transacoes[forma] = formas_transacoes.get(forma, 0) + 1

                # Fiado e cortesia separadamente
                if forma.upper() in ["FIADO", "CORTESIA"]:
                    chave = (nome, forma)
                    fiado_cortesia[chave] = fiado_cortesia.get(chave, 0.0) + valor

            self.label_total_qtd.setText(f"Total Vendidos: {total_itens_vendidos} itens")
            self.label_total_valor.setText(f"Total Pago: R$ {total_valor_pago:.2f}")

            self._preencher_tabela_qtd(self.tabela_qtd, vendidos, cortesia)
            self._preencher_tabela_valor(self.tabela_valor, produtos_valor)
            self._preencher_tabela_formas(self.tabela_formas, formas_valor, formas_transacoes)
            self._preencher_tabela_fiado_cortesia(self.tabela_fiado, fiado_cortesia)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados:\n{e}")

    def _preencher_tabela_qtd(self, tabela, vendidos: dict, cortesia: dict):
        tabela.setRowCount(0)
        todos_produtos = set(vendidos.keys()) | set(cortesia.keys())
        for idx, produto in enumerate(sorted(todos_produtos)):
            vendidos_qtd = vendidos.get(produto, 0)
            cortesia_qtd = cortesia.get(produto, 0)
            tabela.insertRow(idx)
            tabela.setItem(idx, 0, QTableWidgetItem(str(produto)))
            tabela.setItem(idx, 1, QTableWidgetItem(str(vendidos_qtd)))
            tabela.setItem(idx, 2, QTableWidgetItem(str(cortesia_qtd)))

    def _preencher_tabela_valor(self, tabela, produtos_valor: dict):
        tabela.setRowCount(0)
        for idx, (produto, valor) in enumerate(sorted(produtos_valor.items(), key=lambda x: x[1], reverse=True)):
            tabela.insertRow(idx)
            tabela.setItem(idx, 0, QTableWidgetItem(produto))
            item_valor = QTableWidgetItem(f"R$ {valor:.2f}")
            item_valor.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabela.setItem(idx, 1, item_valor)

    def _preencher_tabela_formas(self, tabela, formas_valor: dict, formas_transacoes: dict):
        tabela.setRowCount(0)
        for idx, forma in enumerate(sorted(formas_valor.keys())):
            valor_total = formas_valor[forma]
            qtd_transacoes = formas_transacoes.get(forma, 0)

            tabela.insertRow(idx)
            tabela.setItem(idx, 0, QTableWidgetItem(str(forma)))
            item_valor = QTableWidgetItem(f"R$ {valor_total:.2f}")
            item_valor.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabela.setItem(idx, 1, item_valor)

            item_qtd = QTableWidgetItem(str(qtd_transacoes))
            item_qtd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabela.setItem(idx, 2, item_qtd)

    def _preencher_tabela_fiado_cortesia(self, tabela, dados: dict):
        tabela.setRowCount(0)
        for idx, ((nome, forma), valor) in enumerate(sorted(dados.items())):
            tabela.insertRow(idx)
            tabela.setItem(idx, 0, QTableWidgetItem(nome))
            tabela.setItem(idx, 1, QTableWidgetItem(forma))
            item_valor = QTableWidgetItem(f"R$ {valor:.2f}")
            item_valor.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabela.setItem(idx, 2, item_valor)
