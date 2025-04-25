from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt


class TelaAdminMenu(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        titulo = QLabel("Menu Administrativo")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        # Lista de botões de navegação
        botoes = [
            ("Cadastrar Produto", "TelaCadastroProduto"),
            ("Editar Produto", "TelaEditarProduto"),
            ("Controle de Estoque", "TelaEstoque"),
            ("Visualizar Estoque", "TelaVisualizarEstoque"),
            ("Relatório de Vendas", "TelaRelatorioVendas"),
            ("Relatório de Estornos", "TelaRelatorioEstornos"),
            ("Voltar ao Login", "TelaLogin"),
        ]

        for texto, tela in botoes:
            btn = QPushButton(texto)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3f80ff;
                    color: white;
                    padding: 10px;
                    font-weight: bold;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #5a95ff;
                }
            """)
            btn.clicked.connect(lambda _, t=tela: self.controller.trocar_tela(t))
            layout.addWidget(btn)

        # Botão de sair
        btn_sair = QPushButton("Salvar e Fechar Sistema")
        btn_sair.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        btn_sair.clicked.connect(self.fechar_sistema)
        layout.addWidget(btn_sair)

        self.setLayout(layout)

    def fechar_sistema(self):
        confirm = QMessageBox.question(
            self,
            "Sair",
            "Deseja salvar e fechar o sistema?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.controller.close()
