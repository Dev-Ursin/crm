import streamlit as st
from core.auth import auth_init, sign_in, sign_up, sign_out
from core.rbac import get_departamentos, get_role

st.set_page_config(page_title="CRM Público", layout="wide")
auth_init()

st.title("🏛️ CRM Público — CSV + PDF + Auditoria")

with st.sidebar:
    st.subheader("Acesso")
    if st.session_state.get("access_token"):
        st.write(f"Logado: **{st.session_state['user'].email}**")
        if st.button("Logout", use_container_width=True):
            sign_out()
            st.rerun()
    else:
        tab1, tab2 = st.tabs(["Login","Cadastro"])
        with tab1:
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar", use_container_width=True):
                try:
                    sign_in(email, senha)
                    st.rerun()
                except Exception as e:
                    st.error(f"Falha no login: {e}")
        with tab2:
            email = st.text_input("Email (cadastro)", key="reg_email")
            senha = st.text_input("Senha (cadastro)", type="password", key="reg_pass")
            if st.button("Criar conta", use_container_width=True):
                try:
                    sign_up(email, senha)
                    st.success("Conta criada. Confirme email se necessário.")
                except Exception as e:
                    st.error(f"Falha no cadastro: {e}")

if not st.session_state.get("access_token"):
    st.info("Faça login para continuar.")
    st.stop()

deps = get_departamentos()
if not deps:
    st.warning("Você não pertence a nenhum departamento. Um admin precisa te adicionar em 'membros'.")
    st.stop()

opt = {d["nome"]: d["id"] for d in deps}
dep_nome = st.selectbox("Departamento", list(opt.keys()))
dep_id = opt[dep_nome]
st.session_state["departamento_id"] = dep_id

role = get_role(dep_id)
st.success(f"Departamento: **{dep_nome}** | Papel: **{role}**")
st.caption("Abra as páginas no menu lateral.")
