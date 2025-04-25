from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from db import conectar


class TelaLogin(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("Login")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        # Campo CPF
        self.entry_cpf = QLineEdit()
        self.entry_cpf.setPlaceholderText("CPF (apenas números)")
        layout.addWidget(self.entry_cpf)

        # Campo Senha
        self.entry_senha = QLineEdit()
        self.entry_senha.setPlaceholderText("Senha")
        self.entry_senha.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.entry_senha)

        # Botão Entrar
        btn_entrar = QPushButton("Entrar")
        btn_entrar.setStyleSheet("""
            QPushButton {
                background-color: #3f80ff;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5a95ff;
            }
        """)
        btn_entrar.clicked.connect(self.verificar_login)
        layout.addWidget(btn_entrar)

        # Botão Cadastrar-se
        botoes = QHBoxLayout()
        botoes.addStretch()
        btn_cadastrar = QPushButton("Cadastrar-se")
        btn_cadastrar.clicked.connect(lambda: self.controller.trocar_tela("TelaCadastroUsuario"))
        botoes.addWidget(btn_cadastrar)
        layout.addLayout(botoes)

        self.setLayout(layout)

    def verificar_login(self):
        cpf = self.entry_cpf.text().strip()
        senha = self.entry_senha.text().strip()

        if not cpf.isnumeric() and cpf.lower() != "admin":
            QMessageBox.warning(self, "Erro", "CPF inválido. Digite 11 números.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT nome, senha, tipo FROM usuarios WHERE cpf = ?", (cpf,))
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                nome, senha_armazenada, tipo = resultado
                if senha == senha_armazenada:
                    # Salvar sessão
                    self.controller.usuario_logado = nome
                    self.controller.cpf_logado = cpf
                    self.controller.tipo_usuario = tipo

                    QMessageBox.information(self, "Bem-vindo", f"Olá, {nome}!")

                    if tipo.lower() == "administrador":
                        self.controller.trocar_tela("TelaAdminMenu")
                    else:
                        self.controller.trocar_tela("TelaVendas")
                else:
                    QMessageBox.warning(self, "Erro", "Senha incorreta.")
            else:
                QMessageBox.warning(self, "Erro", "Usuário não encontrado.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao verificar login:\n{e}")
