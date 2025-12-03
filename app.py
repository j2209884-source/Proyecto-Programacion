import streamlit as st

from pages import Dashboard_1,Dashboard_2,Dashboard_3


st.set_page_config(page_title="Proyecto Final", layout="wide")

st.title("🌎 Bienvenido al Proyecto Final")
st.sidebar.title("Navegación")

page = st.sidebar.radio("Selecciona una página:", ["Inicio", "Dashboard 1", "Dashboard 2", "Dashboard 3"])

if page == "Inicio":
    st.markdown("Bienvenida e instrucciones...")
    st.write("")
elif page == "Dashboard 1":
    Dashboard_1.app()
elif page == "Dashboard 2":
    Dashboard_2.app()
elif page == "Dashboard 3":
    Dashboard_3.app()
