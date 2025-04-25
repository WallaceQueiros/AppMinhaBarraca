# db.py
import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "quermesse.db")

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