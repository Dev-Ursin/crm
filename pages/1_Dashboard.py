import streamlit as st
import pandas as pd
from core.auth import require_login, sb_authed
from core.rbac import get_role

st.set_page_config(page_title="Dashboard", layout="wide")
require_login()

dep_id = st.session_state.get("departamento_id")
if not dep_id:
    st.error("Selecione um departamento na Home.")
    st.stop()

sb = sb_authed()
role = get_role(dep_id)

st.title("📊 Dashboard")

rows = sb.table("registros").select("status,prioridade").eq("departamento_id", dep_id).execute().data
df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["status","prioridade"])

c1, c2, c3 = st.columns(3)
c1.metric("Total", int(len(df)))
c2.metric("Abertos", int((df["status"]=="aberto").sum()) if not df.empty else 0)
c3.metric("Em andamento", int((df["status"]=="em_andamento").sum()) if not df.empty else 0)

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("Por status")
    st.dataframe(df["status"].value_counts().reset_index(name="qtd"), use_container_width=True, hide_index=True)
with col2:
    st.subheader("Por prioridade")
    st.dataframe(df["prioridade"].value_counts().reset_index(name="qtd"), use_container_width=True, hide_index=True)

st.caption(f"Papel atual: {role}")

