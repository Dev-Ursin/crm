import streamlit as st
from core.auth import require_login, sb_authed
from core.rbac import get_role, can_write
from core.csv_import import parse_csv

st.set_page_config(page_title="Importar CSV", layout="wide")
require_login()

dep_id = st.session_state.get("departamento_id")
if not dep_id:
    st.error("Selecione um departamento na Home.")
    st.stop()

sb = sb_authed()
role = get_role(dep_id)

st.title("⬆️ Importar CSV (Registros)")

file = st.file_uploader("Envie o CSV", type=["csv"])
if not file:
    st.stop()

df = parse_csv(file)
st.dataframe(df.head(50), use_container_width=True, hide_index=True)

if st.button("Importar", disabled=not can_write(role), use_container_width=True):
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "departamento_id": dep_id,
            "protocolo": None if r["protocolo"] is None else str(r["protocolo"]),
            "nome": None if r["nome"] is None else str(r["nome"]),
            "documento": None if r["documento"] is None else str(r["documento"]),
            "assunto": None if r["assunto"] is None else str(r["assunto"]),
            "status": str(r["status"] or "aberto"),
            "prioridade": str(r["prioridade"] or "media"),
            "data_evento": r["data_evento"],
            "payload": r["payload"] if isinstance(r["payload"], dict) else {},
        })

    BATCH = 200
    for i in range(0, len(rows), BATCH):
        sb.table("registros").insert(rows[i:i+BATCH]).execute()

    st.success(f"Importado: {len(rows)} linhas")
    st.rerun()

