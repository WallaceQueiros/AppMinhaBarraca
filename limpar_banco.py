from db import conectar

def limpar_banco():
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Limpar todas as tabelas
        cursor.execute("DELETE FROM vendas")
        cursor.execute("DELETE FROM estoque")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")

        conn.commit()
        conn.close()
        print("✅ Todas as tabelas foram esvaziadas com sucesso.")

    except Exception as e:
        print(f"❌ Erro ao limpar banco de dados: {e}")

if __name__ == "__main__":
    limpar_banco()
