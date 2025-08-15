import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import sqlite3

st.set_page_config(page_title="Controle de Saída de Entrega", layout="centered")

# ================================
# FUNÇÕES PARA BANCO DE DADOS
# ================================
def criar_tabela():
    conn = sqlite3.connect("entregas.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            numero INTEGER PRIMARY KEY,
            cliente TEXT,
            valor REAL,
            forma_pagamento TEXT,
            troco REAL,
            entregador TEXT,
            entregue INTEGER,
            data_hora TEXT
        )
    """)
    conn.commit()
    conn.close()

def adicionar_entrega(numero, cliente, valor, forma_pagamento, troco):
    conn = sqlite3.connect("entregas.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO entregas (numero, cliente, valor, forma_pagamento, troco, entregador, entregue, data_hora) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (numero, cliente, valor, forma_pagamento, troco, None, 0, None)
    )
    conn.commit()
    conn.close()

def atualizar_entrega(numero, entregador):
    conn = sqlite3.connect("entregas.db")
    c = conn.cursor()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute(
        "UPDATE entregas SET entregador=?, entregue=1, data_hora=? WHERE numero=?",
        (entregador, data_hora, numero)
    )
    conn.commit()
    conn.close()

def carregar_entregas():
    conn = sqlite3.connect("entregas.db")
    df = pd.read_sql_query("SELECT * FROM entregas", conn)
    conn.close()
    return df

def limpar_banco():
    conn = sqlite3.connect("entregas.db")
    c = conn.cursor()
    c.execute("DELETE FROM entregas")
    conn.commit()
    conn.close()

# Criar tabela no banco
criar_tabela()

# ================================
# INTERFACE
# ================================

# Logo
st.image("cupim_logo.png", width=250)  # Salve sua logo com o texto atualizado na mesma pasta
st.markdown("<h5 style='text-align:center;'>seu melhor laser em família desde 2005</h5>", unsafe_allow_html=True)
st.title("📦 Controle de Saída de Entrega - Comércio")

# Descobrir número atual
df_banco = carregar_entregas()
if df_banco.empty:
    numero_atual = 1
else:
    numero_atual = df_banco["numero"].max() + 1

# -------------------------
# FORMULÁRIO DE NOVA ENTREGA
# -------------------------
with st.form("form_entrega"):
    st.markdown(f"**Número da Entrega:** `{numero_atual}`")
    
    cliente = st.text_input("Nome do Cliente")
    valor = st.number_input("Valor da Compra (R$)", min_value=0.0, step=0.01, format="%.2f")
    forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "Pix", "Outro"])
    
    troco = None
    if forma_pagamento == "Dinheiro":
        pago = st.number_input("Valor pago pelo cliente (R$)", min_value=0.0, step=0.01, format="%.2f")
        troco = pago - valor
        if pago >= valor:
            st.success(f"💰 Troco a devolver: R$ {troco:.2f}")
        else:
            st.warning("Valor pago é menor que o valor da compra!")
    
    adicionar = st.form_submit_button("✅ Adicionar Pedido")

if adicionar:
    if cliente.strip():
        adicionar_entrega(numero_atual, cliente, valor, forma_pagamento, troco)
        st.success("Pedido adicionado à lista!")
        st.experimental_rerun()
    else:
        st.error("Digite o nome do cliente antes de salvar.")

# -------------------------
# LISTA DE ENTREGAS
# -------------------------
df = carregar_entregas()

if not df.empty:
    st.subheader("📋 Lista de Entregas")

    # Campo de busca
    filtro = st.text_input("🔍 Buscar por número, cliente ou entregador")
    if filtro.strip():
        df = df[df.apply(lambda row: 
                         filtro.lower() in str(row['numero']).lower() 
                         or (row['cliente'] and filtro.lower() in row['cliente'].lower())
                         or (row['entregador'] and filtro.lower() in row['entregador'].lower()), axis=1)]

    for _, entrega in df.iterrows():
        if entrega["entregue"] == 1:
            cor = "background-color: #d4edda;"  # Verde
        else:
            cor = "background-color: #fff3cd;"  # Amarelo

        st.markdown(
            f"""
            <div style="{cor} padding:10px; border-radius:8px; margin-bottom:5px;">
                <b>#{entrega['numero']}</b> | 👤 Cliente: {entrega['cliente']}<br>
                💰 R$ {entrega['valor']:.2f} | 💳 {entrega['forma_pagamento']}<br>
                {f"🚚 Entregador: {entrega['entregador']} | 📅 {entrega['data_hora']} ✅" if entrega['entregue'] == 1 else ""}
            </div>
            """,
            unsafe_allow_html=True
        )

        if entrega["entregue"] == 0:
            entregador_input = st.text_input(
                f"Entregador para #{entrega['numero']}",
                key=f"entregador_{entrega['numero']}"
            )
            if st.button(f"Marcar entregue #{entrega['numero']}", key=f"btn_{entrega['numero']}"):
                if entregador_input.strip():
                    atualizar_entrega(entrega["numero"], entregador_input)
                    st.success(f"Entrega #{entrega['numero']} marcada como concluída!")
                    st.experimental_rerun()
                else:
                    st.error("Digite o nome do entregador antes de confirmar.")

    # Exportar Excel
    def gerar_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Entregas")
        return output.getvalue()

    excel_data = gerar_excel(df)
    st.download_button(
        label="⬇️ Baixar Lista em Excel",
        data=excel_data,
        file_name="controle_entregas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Limpar tudo
    if st.button("🗑️ Limpar Lista"):
        limpar_banco()
        st.experimental_rerun()
     
   
