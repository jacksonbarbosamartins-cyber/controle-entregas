import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Controle de Entregas", layout="wide")

# Carregar dados na sessão
if "entregas" not in st.session_state:
    st.session_state.entregas = pd.DataFrame(columns=[
        "Nº", "Nome do cliente", "Valor da compra", 
        "Valor pago pelo cliente", "Tipo de pagamento", 
        "Nome do entregador", "Entregue", "Horário"
    ])
    st.session_state.proximo_id = 1

# Formulário para adicionar nova entrega
with st.form("nova_entrega"):
    nome = st.text_input("Nome do cliente")
    valor_compra = st.number_input("Valor da compra", min_value=0.0, step=1.0, format="%.2f")
    valor_pago = st.number_input("Valor pago pelo cliente", min_value=0.0, step=1.0, format="%.2f")
    pagamento = st.selectbox("Tipo de pagamento", ["Dinheiro", "Pix", "Cartão"])
    entregador = st.text_input("Nome do entregador (pode preencher depois)")
    enviar = st.form_submit_button("Adicionar")

    if enviar and nome:
        nova = {
            "Nº": st.session_state.proximo_id,
            "Nome do cliente": nome,
            "Valor da compra": valor_compra,
            "Valor pago pelo cliente": valor_pago,
            "Tipo de pagamento": pagamento,
            "Nome do entregador": entregador,
            "Entregue": False,
            "Horário": ""
        }
        st.session_state.entregas = pd.concat(
            [st.session_state.entregas, pd.DataFrame([nova])],
            ignore_index=True
        )
        st.session_state.proximo_id += 1

st.subheader("📋 Lista de Entregas")

# Editor de tabela estilo Excel
df_editado = st.data_editor(
    st.session_state.entregas,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)

# Atualizar dados editados
st.session_state.entregas = df_editado.copy()

# Marcar horário quando a entrega for concluída
for i, row in st.session_state.entregas.iterrows():
    if row["Entregue"] and row["Horário"] == "":
        st.session_state.entregas.at[i, "Horário"] = datetime.now().strftime("%H:%M:%S")

# Exportar para Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Entregas")
    return output.getvalue()

excel_data = to_excel(st.session_state.entregas)
st.download_button(
    label="📥 Exportar para Excel",
    data=excel_data,
    file_name="lista_entregas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
