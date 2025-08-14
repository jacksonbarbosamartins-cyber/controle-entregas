import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Controle de Saída de Entrega", layout="centered")

st.title("📦 Controle de Saída de Entrega - Comércio")

# Criar sessão para armazenar dados
if "entregas" not in st.session_state:
    st.session_state.entregas = []
if "numero_atual" not in st.session_state:
    st.session_state.numero_atual = 1  # Número da entrega automático

# Formulário
with st.form("form_entrega"):
    numero = st.session_state.numero_atual
    st.write(f"**Número da Entrega:** {numero}")
    
    valor = st.number_input("Valor da Compra (R$)", min_value=0.0, step=0.01, format="%.2f")
    forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "Pix", "Outro"])
    
    troco = None
    if forma_pagamento == "Dinheiro":
        pago = st.number_input("Valor pago pelo cliente (R$)", min_value=0.0, step=0.01, format="%.2f")
        troco = pago - valor
        st.write(f"💰 Troco a devolver: **R$ {troco:.2f}**")
    
    entregador = st.text_input("Nome do Entregador")
    entregue = st.checkbox("Entrega efetuada?")
    
    adicionar = st.form_submit_button("Adicionar à Lista")

# Quando clicar no botão, adiciona os dados
if adicionar:
    if entregador.strip() != "":
        registro = {
            "Número": numero,
            "Valor (R$)": f"{valor:.2f}",
            "Forma de Pagamento": forma_pagamento,
            "Entregador": entregador,
            "Entregue": "Sim" if entregue else "Não"
        }
        if forma_pagamento == "Dinheiro":
            registro["Troco (R$)"] = f"{troco:.2f}"
        st.session_state.entregas.append(registro)
        st.session_state.numero_atual += 1  # Incrementa número automaticamente
        st.success("Entrega adicionada com sucesso!")
    else:
        st.error("Preencha o nome do entregador.")

# Mostrar tabela de entregas
if st.session_state.entregas:
    df = pd.DataFrame(st.session_state.entregas)
    st.subheader("📋 Lista de Entregas")
    st.table(df)

    # Função para gerar Excel
    def gerar_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Entregas")
        return output.getvalue()

    # Botão para download
    excel_data = gerar_excel(df)
    st.download_button(
        label="⬇️ Baixar Lista em Excel",
        data=excel_data,
        file_name="controle_entregas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )