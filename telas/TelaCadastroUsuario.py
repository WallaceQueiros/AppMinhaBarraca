from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from db import conectar


class TelaCadastroUsuario(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.combo_tipo = None
        self.entry_senha = None
        self.entry_cpf = None
        self.entry_nome = None
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        titulo = QLabel("Cadastro de Usuário")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        # Campos
        self.entry_nome = QLineEdit()
        self.entry_nome.setPlaceholderText("Nome")
        layout.addWidget(self.entry_nome)

        self.entry_cpf = QLineEdit()
        self.entry_cpf.setPlaceholderText("CPF (somente números)")
        layout.addWidget(self.entry_cpf)

        self.entry_senha = QLineEdit()
        self.entry_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_senha.setPlaceholderText("Senha")
        layout.addWidget(self.entry_senha)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Comum", "Administrador"])
        self.combo_tipo.setPlaceholderText("Tipo de usuário")
        layout.addWidget(self.combo_tipo)

        # Botão Cadastrar
        btn_cadastrar = QPushButton("Cadastrar")
        btn_cadastrar.setStyleSheet("""
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
        btn_cadastrar.clicked.connect(self.cadastrar_usuario)
        layout.addWidget(btn_cadastrar)

        # Botões inferiores alinhados
        btns = QHBoxLayout()
        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(lambda: self.controller.trocar_tela("TelaLogin"))
        btns.addStretch()
        btns.addWidget(btn_voltar)
        layout.addLayout(btns)

        self.setLayout(layout)

    def cadastrar_usuario(self):
        nome = self.entry_nome.text().strip()
        cpf = self.entry_cpf.text().strip()
        senha = self.entry_senha.text().strip()
        tipo = self.combo_tipo.currentText()

        if not nome or not cpf or not senha:
            QMessageBox.warning(self, "Erro", "Todos os campos são obrigatórios.")
            return

        if not cpf.isnumeric() or len(cpf) != 11:
            QMessageBox.warning(self, "Erro", "CPF deve conter 11 números.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Erro", "CPF já cadastrado.")
                conn.close()
                return

            cursor.execute("INSERT INTO usuarios (nome, cpf, senha, tipo) VALUES (?, ?, ?, ?)",
                           (nome, cpf, senha, tipo))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sucesso", "Usuário cadastrado com sucesso!")

            # Limpa os campos
            self.entry_nome.clear()
            self.entry_cpf.clear()
            self.entry_senha.clear()
            self.combo_tipo.setCurrentIndex(0)

            # Opcional: volta para a tela de login
            self.controller.trocar_tela("TelaLogin")


        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao cadastrar usuário:\n{e}")
