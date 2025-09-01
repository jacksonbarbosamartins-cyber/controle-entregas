
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO

# ============================
# CONFIGURAÇÃO DA PÁGINA
# ============================
st.set_page_config(page_title="Controle de Entregas", layout="wide")

# ============================
# BANCO DE DADOS
# ============================
def criar_tabela():
    conn = sqlite3.connect("entregas.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER,
            cliente TEXT,
            valor_compra REAL,
            valor_pago REAL,
            forma_pagamento TEXT,
            entregador TEXT,
            entregue INTEGER DEFAULT 0,
            horario_entrega TEXT
        )
    """)
    conn.commit()
    conn.close()

def carregar_entregas():
    conn = sqlite3.connect("entregas.db")
    df = pd.read_sql_query("SELECT * FROM entregas", conn)
    conn.close()
    return df

def salvar_entrega(cliente, valor_compra, valor_pago, forma_pagamento, entregador):
    conn = sqlite3.connect("entregas.db")
    c = conn.cursor()
    c.execute("SELECT MAX(numero) FROM entregas")
    ultimo_numero = c.fetchone()[0]
    if ultimo_numero is None:
        ultimo_numero = 0
    numero = ultimo_numero + 1

    c.execute("""
        INSERT INTO entregas (numero, cliente, valor_compra, valor_pago, forma_pagamento, entregador, entregue, horario_entrega)
        VALUES (?, ?, ?, ?, ?, ?, 0, NULL)
    """, (numero, cliente, valor_compra, valor_pago, forma_pagamento, entregador))

    conn.commit()
    conn.close()

def atualizar_entrega(id, campo, valor):
    conn = sqlite3.connect("entregas.db")
    c = conn.cursor()
    c.execute(f"UPDATE entregas SET {campo}=? WHERE id=?", (valor, id))
    conn.commit()
    conn.close()

def limpar_entregas():
    conn = sqlite3.connect("entregas.db")
    c = conn.cursor()
    c.execute("DELETE FROM entregas")
    conn.commit()
    conn.close()

# ============================
# APP
# ============================
criar_tabela()

st.title("📦 Controle de Entregas")

# Formulário de cadastro
with st.form("nova_entrega"):
    st.subheader("Adicionar Nova Entrega")
    cliente = st.text_input("Nome do Cliente")
    valor_compra = st.number_input("Valor da Compra (R$)", step=1.0, format="%.2f")
    valor_pago = st.number_input("Valor Pago (R$)", step=1.0, format="%.2f")
    forma_pagamento = st.selectbox("Forma de Pagamento", ["", "Dinheiro", "Pix", "Cartão"])
    entregador = st.text_input("Nome do Entregador")

    submit = st.form_submit_button("Adicionar")

    if submit and cliente:
        salvar_entrega(cliente, valor_compra, valor_pago, forma_pagamento, entregador)
        st.success("Entrega adicionada com sucesso!")
        st.rerun()

# ============================
# LISTA DE ENTREGAS
# ============================
st.subheader("📋 Lista de Entregas")

df = carregar_entregas()

if not df.empty:
    for index, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1,2,2,2,2,2,2,2])

            col1.write(f"#{row['numero']}")
            cliente_edit = col2.text_input("Cliente", value=row["cliente"], key=f"cliente_{row['id']}")
            valor_compra_edit = col3.number_input("Valor Compra", value=row["valor_compra"] if row["valor_compra"] else 0.0, step=1.0, format="%.2f", key=f"compra_{row['id']}")
            valor_pago_edit = col4.number_input("Valor Pago", value=row["valor_pago"] if row["valor_pago"] else 0.0, step=1.0, format="%.2f", key=f"pago_{row['id']}")
            forma_pagamento_edit = col5.text_input("Forma Pgto", value=row["forma_pagamento"] if row["forma_pagamento"] else "", key=f"pgto_{row['id']}")
            entregador_edit = col6.text_input("Entregador", value=row["entregador"] if row["entregador"] else "", key=f"entregador_{row['id']}")

            entregue_edit = col7.checkbox("Entregue", value=bool(row["entregue"]), key=f"check_{row['id']}")
            horario = row["horario_entrega"] if row["horario_entrega"] else ""
            col8.write(horario)

            if cliente_edit != row["cliente"]:
                atualizar_entrega(row["id"], "cliente", cliente_edit)
            if valor_compra_edit != row["valor_compra"]:
                atualizar_entrega(row["id"], "valor_compra", valor_compra_edit)
            if valor_pago_edit != row["valor_pago"]:
                atualizar_entrega(row["id"], "valor_pago", valor_pago_edit)
            if forma_pagamento_edit != row["forma_pagamento"]:
                atualizar_entrega(row["id"], "forma_pagamento", forma_pagamento_edit)
            if entregador_edit != row["entregador"]:
                atualizar_entrega(row["id"], "entregador", entregador_edit)
            if entregue_edit != row["entregue"]:
                atualizar_entrega(row["id"], "entregue", int(entregue_edit))
                if entregue_edit:
                    atualizar_entrega(row["id"], "horario_entrega", datetime.now().strftime("%H:%M:%S"))

    # Exportar para Excel
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("⬇️ Exportar para Excel", data=buffer, file_name="entregas.xlsx", mime="application/vnd.ms-excel")

    # Botão de limpar
    if st.button("🗑️ Limpar Lista"):
        limpar_entregas()
        st.warning("Lista de entregas apagada!")
        st.rerun()

else:
    st.info("Nenhuma entrega cadastrada ainda.")
