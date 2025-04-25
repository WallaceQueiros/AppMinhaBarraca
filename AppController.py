from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QPushButton
)

from PyQt6.QtCore import Qt
import sys

# IMPORTS DAS TELAS
from telas.TelaLogin import TelaLogin
from telas.TelaCadastroUsuario import TelaCadastroUsuario
from telas.TelaAdminMenu import TelaAdminMenu
from telas.TelaVendas import TelaVendas
from telas.TelaCadastroProduto import TelaCadastroProduto
from telas.TelaEditarProduto import TelaEditarProduto
from telas.TelaEstoque import TelaEstoque
from telas.TelaRelatorioVendas import TelaRelatorioVendas
from telas.TelaVisualizarEstoque import TelaVisualizarEstoque
from telas.TelaEstornoVendas import TelaEstornoVendas
from telas.TelaRelatorioEstornos import TelaRelatorioEstornos

# IMPORTA OS TEMAS
from themes import light_theme, dark_theme


class AppController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Quermesse")
        self.setGeometry(100, 100, 800, 600)

        # Sessão do usuário logado
        self.usuario_logado = None
        self.cpf_logado = None
        self.tipo_usuario = None

        # Modo escuro habilitado?
        self.tema_escuro = False

        # Stack central com as telas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Botão de troca de tema
        self.botao_tema = QPushButton("🌙 Escuro", self)
        self.botao_tema.setFixedSize(100, 40)
        self.botao_tema.move(self.width() - 120, 10)
        self.botao_tema.clicked.connect(self.trocar_tema)
        self.botao_tema.raise_()

        # Posicionamento responsivo
        self.resizeEvent = self.centralizar_botao_tema

        # Registro de telas
        self.telas = {}
        self.registrar_tela("TelaLogin", TelaLogin(self))
        self.registrar_tela("TelaCadastroUsuario", TelaCadastroUsuario(self))
        self.registrar_tela("TelaAdminMenu", TelaAdminMenu(self))
        self.registrar_tela("TelaVendas", TelaVendas(self))
        self.registrar_tela("TelaCadastroProduto", TelaCadastroProduto(self))
        self.registrar_tela("TelaEditarProduto", TelaEditarProduto(self))
        self.registrar_tela("TelaEstoque", TelaEstoque(self))
        self.registrar_tela("TelaRelatorioVendas", TelaRelatorioVendas(self))
        self.registrar_tela("TelaVisualizarEstoque", TelaVisualizarEstoque(self))
        self.registrar_tela("TelaEstornoVendas", TelaEstornoVendas(self))
        self.registrar_tela("TelaRelatorioEstornos", TelaRelatorioEstornos(self))

        self.trocar_tela("TelaLogin")
        self.aplicar_tema()

    def registrar_tela(self, nome: str, widget: QWidget):
        self.telas[nome] = widget
        self.stacked_widget.addWidget(widget)

    def trocar_tela(self, nome: str):
        widget = self.telas.get(nome)
        if widget:
            self.stacked_widget.setCurrentWidget(widget)

    def aplicar_tema(self):
        estilo = dark_theme if self.tema_escuro else light_theme
        self.setStyleSheet(estilo)
        self.botao_tema.setText("☀️ Claro" if self.tema_escuro else "🌙 Escuro")

    def trocar_tema(self):
        self.tema_escuro = not self.tema_escuro
        self.aplicar_tema()

    def centralizar_botao_tema(self, event):
        self.botao_tema.move(self.width() - 120, 10)


# PONTO DE ENTRADA
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppController()
    window.show()
    sys.exit(app.exec())



