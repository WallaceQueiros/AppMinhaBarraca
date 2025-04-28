# db.py
import sqlite3
import os
import sys

def resource_path(relative_path):
    """Retorna o caminho correto para recursos, funcionando tanto em .py quanto em .exe"""
    try:
        base_path = sys._MEIPASS  # Usado quando empacotado no PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")  # Usado quando rodando direto no PyCharm
    return os.path.join(base_path, relative_path)

DB_PATH = resource_path("quermesse.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT DEFAULT 'Comum'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descricao TEXT,
            valor_venda REAL,
            valor_custo REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_produto TEXT NOT NULL,
            estoque_inicial INTEGER DEFAULT 0,
            adicional INTEGER DEFAULT 0,
            vendido INTEGER DEFAULT 0,
            estoque_atual INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT,
            cpf_cliente TEXT,
            produto TEXT,
            valor REAL,
            forma_pagamento TEXT,
            data_venda TEXT
        )
    """)

    conn.commit()
    conn.close()
