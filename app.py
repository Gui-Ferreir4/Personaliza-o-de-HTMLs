import streamlit as st
import pandas as pd
import re

# =========================
# Funções principais
# =========================
def substituir_tags(template_html, linha):
    """
    Substitui as TAGs no HTML com os valores do CSV.
    Se o valor estiver vazio, substitui por string vazia.
    """
    resultado = template_html
    for coluna, valor in linha.items():
        placeholder = f"##{coluna}##"
        if pd.isna(valor):
            valor = ""  # Substitui vazio
        resultado = resultado.replace(placeholder, str(valor))
    return resultado

def gerar_html_unico(df, template_html):
    """
    Gera um único HTML com todas as linhas do CSV.
    """
    html_final = ""
    for _, linha in df.iterrows():
        html_final += substituir_tags(template_html, linha) + "\n\n"
    return html_final

def gerar_varios_htmls(df, template_html):
    """
    Gera vários HTMLs, um por linha do CSV.
    """
    htmls = []
    for _, linha in df.iterrows():
        htmls.append(substituir_tags(template_html, linha))
    return htmls

# =========================
# Layout do App
# =========================
st.set_page_config(page_title="Gerador de HTMLs", layout="wide")
st.title("📧 Gerador de HTMLs a partir de CSV")

st.markdown("Este aplicativo lê um **CSV com ofertas** e substitui as **TAGs do HTML** pelos valores correspondentes.")

# Uploads
uploaded_csv = st.file_uploader("Carregar arquivo CSV", type=["csv"])
uploaded_html = st.file_uploader("Carregar arquivo HTML (modelo)", type=["html", "htm"])

# Seleção de modo
modo_saida = st.radio(
    "📌 Selecione o modo de saída:",
    ["Um único HTML (todas as linhas)", "Vários HTMLs (um por linha do CSV)"],
    help="Defina como deseja gerar o(s) HTML(s)."
)

# =========================
# Explicação do Modo Único
# =========================
if modo_saida == "Um único HTML (todas as linhas)":
    st.subheader("📖 Como funciona este modo?")
    st.markdown("""
    No modo **Um único HTML (todas as linhas)**, o aplicativo pega cada linha do CSV,
    substitui as TAGs correspondentes no template, e junta tudo em um **único HTML consolidado**.
    
    Isso é útil quando você deseja ter **várias ofertas em uma mesma página** ou e-mail.
    """)

    # Exemplo de tabela colorida
    st.markdown("### 🔎 Exemplo de funcionamento")
    st.markdown("""
    Abaixo, um exemplo simplificado com 3 linhas do CSV aplicadas ao mesmo HTML:
    """)
    
    st.markdown("""
    <table style="border-collapse: collapse; width: 100%; text-align: center;">
      <tr>
        <th style="border: 1px solid black; padding: 8px; background-color: #f4cccc;">##TITULO##</th>
        <th style="border: 1px solid black; padding: 8px; background-color: #cfe2f3;">##PRECO##</th>
        <th style="border: 1px solid black; padding: 8px; background-color: #d9ead3;">##DESCRICAO##</th>
      </tr>
      <tr>
        <td style="border: 1px solid black; padding: 8px;">Oferta A</td>
        <td style="border: 1px solid black; padding: 8px;">R$ 100</td>
        <td style="border: 1px solid black; padding: 8px;">Descrição da Oferta A</td>
      </tr>
      <tr>
        <td style="border: 1px solid black; padding: 8px;">Oferta B</td>
        <td style="border: 1px solid black; padding: 8px;">R$ 200</td>
        <td style="border: 1px solid black; padding: 8px;">Descrição da Oferta B</td>
      </tr>
      <tr>
        <td style="border: 1px solid black; padding: 8px;">Oferta C</td>
        <td style="border: 1px solid black; padding: 8px;">R$ 300</td>
        <td style="border: 1px solid black; padding: 8px;">Descrição da Oferta C</td>
      </tr>
    </table>
    """, unsafe_allow_html=True)

    # Legenda
    st.markdown("""
    **Legenda de cores:**
    - 🟥 Vermelho claro → **##TITULO##** (será substituído pelo título da oferta)  
    - 🟦 Azul claro → **##PRECO##** (será substituído pelo preço da oferta)  
    - 🟩 Verde claro → **##DESCRICAO##** (será substituído pela descrição da oferta)  
    """)

# =========================
# Processamento principal
# =========================
if uploaded_csv and uploaded_html:
    df = pd.read_csv(uploaded_csv, sep=";", dtype=str)  # Lê CSV como string
    template_html = uploaded_html.read().decode("utf-8")

    st.subheader("📊 Pré-visualização do CSV")
    st.dataframe(df.head())

    if st.button("🚀 Gerar HTML"):
        if modo_saida == "Um único HTML (todas as linhas)":
            resultado = gerar_html_unico(df, template_html)
            st.download_button("📥 Baixar HTML Consolidado", data=resultado, file_name="resultado.html", mime="text/html")
            st.code(resultado[:1000] + "...", language="html")

        elif modo_saida == "Vários HTMLs (um por linha do CSV)":
            htmls = gerar_varios_htmls(df, template_html)
            for i, html in enumerate(htmls, start=1):
                st.download_button(f"📥 Baixar HTML {i}", data=html, file_name=f"resultado_{i}.html", mime="text/html")
                st.code(html[:500] + "...", language="html")
