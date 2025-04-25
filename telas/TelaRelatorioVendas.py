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

        titulo = QLabel("Relatório de vendas")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(titulo)

        layout_secoes = QHBoxLayout()
        layout_secoes.setSpacing(20)

        # --- Produtos em Quantidade ---
        grupo_qtd = QGroupBox("Produtos (Quantidade)")
        layout_qtd = QVBoxLayout()
        self.label_total_qtd = QLabel("Total: 0 itens")
        self.label_total_qtd.setStyleSheet("color: blue; font-weight: bold;")
        layout_qtd.addWidget(self.label_total_qtd, alignment=Qt.AlignmentFlag.AlignCenter)

        self.tabela_qtd = QTableWidget()
        self.tabela_qtd.setColumnCount(2)
        self.tabela_qtd.setHorizontalHeaderLabels(["Produto", "Quantidade"])
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

        # Botão de Voltar
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

            total_qtd = 0
            total_valor = 0.0
            produtos_qtd = {}
            produtos_valor = {}
            formas_valor = {}
            formas_transacoes = {}  # novo
            fiado_cortesia = {}

            transacoes_contadas = set()  # set para guardar transações únicas

            for nome, produto, valor, forma, data in vendas:
                total_qtd += 1
                produtos_qtd[produto] = produtos_qtd.get(produto, 0) + 1
                produtos_valor[produto] = produtos_valor.get(produto, 0.0) + valor
                formas_valor[forma] = formas_valor.get(forma, 0.0) + valor

                transacao_id = f"{nome}-{forma}-{data.split()[0]}"  # único por dia
                if transacao_id not in transacoes_contadas:
                    transacoes_contadas.add(transacao_id)
                    formas_transacoes[forma] = formas_transacoes.get(forma, 0) + 1

                if forma.upper() in ["FIADO", "CORTESIA"]:
                    chave = (nome, forma)
                    fiado_cortesia[chave] = fiado_cortesia.get(chave, 0.0) + valor
                else:
                    total_valor += valor

            self.label_total_qtd.setText(f"Total: {total_qtd} itens")
            self.label_total_valor.setText(f"Total Pago: R$ {total_valor:.2f}")

            self._preencher_tabela(self.tabela_qtd, produtos_qtd, qtd=True)
            self._preencher_tabela(self.tabela_valor, produtos_valor, qtd=False)
            self._preencher_tabela_formas(self.tabela_formas, formas_valor, formas_transacoes)
            self._preencher_tabela_fiado_com_forma(self.tabela_fiado, fiado_cortesia)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados:\n{e}")

    def _preencher_tabela(self, tabela, dados: dict, qtd: bool):
        tabela.setRowCount(0)

        # Ordenar decrescente por valor (apenas se for de quantidade)
        sorted_items = sorted(
            dados.items(),
            key=lambda item: item[1],
            reverse=qtd
        )

        for idx, (chave, valor) in enumerate(sorted_items):
            tabela.insertRow(idx)
            tabela.setItem(idx, 0, QTableWidgetItem(str(chave)))
            if qtd:
                tabela.setItem(idx, 1, QTableWidgetItem(str(valor)))
            else:
                item_valor = QTableWidgetItem(f"R$ {valor:.2f}")
                item_valor.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                tabela.setItem(idx, 1, item_valor)

    def _preencher_tabela_formas(self, tabela, valores: dict, quantidades: dict):
        tabela.setRowCount(0)
        for idx, forma in enumerate(sorted(valores.keys())):
            valor_total = valores[forma]
            qtd = quantidades.get(forma, 0)

            tabela.insertRow(idx)
            tabela.setItem(idx, 0, QTableWidgetItem(str(forma)))

            item_valor = QTableWidgetItem(f"R$ {valor_total:.2f}")
            item_valor.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabela.setItem(idx, 1, item_valor)

            item_qtd = QTableWidgetItem(str(qtd))
            item_qtd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabela.setItem(idx, 2, item_qtd)

    def _preencher_tabela_fiado_com_forma(self, tabela, dados: dict):
        tabela.setRowCount(0)
        for idx, ((nome, forma), valor) in enumerate(sorted(dados.items())):
            tabela.insertRow(idx)
            tabela.setItem(idx, 0, QTableWidgetItem(str(nome)))
            tabela.setItem(idx, 1, QTableWidgetItem(str(forma)))
            item_valor = QTableWidgetItem(f"R$ {valor:.2f}")
            item_valor.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabela.setItem(idx, 2, item_valor)
