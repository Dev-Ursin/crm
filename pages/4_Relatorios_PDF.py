import streamlit as st
from core.auth import require_login, sb_authed
from core.pdf_reports import build_pdf

st.set_page_config(page_title="Relatórios PDF", layout="wide")
require_login()

dep_id = st.session_state.get("departamento_id")
if not dep_id:
    st.error("Selecione um departamento na Home.")
    st.stop()

sb = sb_authed()
st.title("📄 Relatório PDF")

status = st.selectbox("Status", ["(todos)","aberto","em_andamento","resolvido","arquivado"])
prioridade = st.selectbox("Prioridade", ["(todas)","baixa","media","alta"])
limite = st.number_input("Limite", 50, 5000, 500, 50)

q = sb.table("registros").select("protocolo,nome,status,prioridade").eq("departamento_id", dep_id).order("created_at", desc=True).limit(int(limite))
if status != "(todos)":
    q = q.eq("status", status)
if prioridade != "(todas)":
    q = q.eq("prioridade", prioridade)

rows = q.execute().data
st.write(f"Linhas: **{len(rows)}**")

if st.button("Gerar PDF", use_container_width=True):
    subtitle = f"Filtros: status={status}, prioridade={prioridade}"
    pdf = build_pdf("Relatório de Registros", subtitle, rows)
    st.download_button("Baixar PDF", data=pdf, file_name="relatorio.pdf", mime="application/pdf", use_container_width=True)

