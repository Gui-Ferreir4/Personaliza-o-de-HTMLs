import pandas as pd
import re
import streamlit as st
import io
import zipfile

st.set_page_config(page_title="Personalizar HTML", layout="wide")

st.title("📄 Personalizar HTML com CSV")

st.markdown("""
Este app substitui **TAGs personalizadas** em um arquivo HTML com valores de um arquivo CSV.
- As TAGs devem estar no formato `<#Coluna01>`, `<#Coluna02>`, etc.
- O CSV deve conter os nomes das colunas correspondentes às TAGs.
- Quando o dado estiver **vazio**, ele será substituído por **vazio** no HTML.
""")

# Escolher separador
sep = st.radio("Selecione o separador do CSV:", options=[";", ","], horizontal=True)

# Upload dos arquivos
arquivo_csv = st.file_uploader("📄 Selecione o arquivo CSV", type=["csv"])
arquivo_html = st.file_uploader("🌐 Selecione o arquivo HTML", type=["html", "htm"])

# Função para substituir tags
def substituir_tags(conteudo_html, dados_csv):
    substituicoes = []
    for linha in range(len(dados_csv)):
        for coluna in dados_csv.columns:
            tag = f'<#{coluna}{"{:02d}".format(linha + 1)}>'
            valor = "" if pd.isna(dados_csv[coluna].iloc[linha]) else str(dados_csv[coluna].iloc[linha])
            novo_html, n_subs = re.subn(re.escape(tag), valor, conteudo_html)
            conteudo_html = novo_html
            substituicoes.append({
                "Linha CSV": linha + 1,
                "Coluna": coluna,
                "Tag": tag,
                "Valor Substituído": valor,
                "Qtd. Substituições": n_subs
            })
    return conteudo_html, pd.DataFrame(substituicoes)

if arquivo_csv and arquivo_html:
    try:
        # Resetar ponteiro do CSV e ler
        arquivo_csv.seek(0)
        dados_csv = pd.read_csv(arquivo_csv, sep=sep)
        dados_csv.columns = [col.strip() for col in dados_csv.columns]

        # Ler HTML corretamente (sem perder buffer)
        conteudo_html = arquivo_html.getvalue().decode("utf-8")

        modo = st.radio(
            "Modo de saída:",
            ["🔹 Um único HTML (todas as linhas)", "🔹 Vários HTMLs (um por linha do CSV)"]
        )

        if st.button("🚀 Modificar HTML"):
            if modo.startswith("🔹 Um único"):
                conteudo_modificado, relatorio = substituir_tags(conteudo_html, dados_csv)

                st.success("✅ HTML modificado com sucesso!")
                st.download_button(
                    label="📥 Baixar HTML modificado",
                    data=conteudo_modificado,
                    file_name=f"personalizado_{arquivo_html.name}",
                    mime="text/html"
                )

                # Tabs para visualizar resultados
                tab1, tab2, tab3 = st.tabs(["📊 Relatório", "🔎 Código HTML", "🌐 Preview"])
                with tab1:
                    st.dataframe(relatorio)
                with tab2:
                    st.code(conteudo_modificado, language="html")
                with tab3:
                    st.components.v1.html(conteudo_modificado, height=500, scrolling=True)

            else:
                arquivos_zip = io.BytesIO()
                with zipfile.ZipFile(arquivos_zip, mode="w") as zf:
                    for i in range(len(dados_csv)):
                        html_linha, _ = substituir_tags(conteudo_html, dados_csv.iloc[[i]])
                        nome_arquivo = f"personalizado_linha{i+1}_{arquivo_html.name}"
                        zf.writestr(nome_arquivo, html_linha)
                arquivos_zip.seek(0)

                st.success("✅ HTMLs individuais gerados com sucesso!")
                st.download_button(
                    label="📥 Baixar ZIP com todos os HTMLs",
                    data=arquivos_zip,
                    file_name="htmls_personalizados.zip",
                    mime="application/zip"
                )

    except pd.errors.EmptyDataError:
        st.error("❌ O arquivo CSV está vazio ou inválido.")
    except pd.errors.ParserError:
        st.error("❌ Erro ao analisar o CSV. Verifique o separador.")
    except Exception as e:
        st.error(f"⚠️ Erro inesperado: {str(e)}")
