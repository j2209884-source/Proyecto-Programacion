import streamlit as st

from pages import a.py

st.set_page_config(page_title="Proyecto Final", layout="wide")

st.title("🌎 Bienvenido al Proyecto Final")
st.sidebar.title("Navegación")

page = st.sidebar.radio("Selecciona una página:", ["Inicio", "Dashboard 1", "Dashboard 2", "Dashboard 3"])

if page == "Inicio":
    st.markdown("Bienvenida e instrucciones...")
    st.write("")
elif page == "Dashboard 1":
    a.py.app()   # función que creaste dentro de dashboard1.py
elif page == "Dashboard 2":
    dashboard2.app()
elif page == "Dashboard 3":
    dashboard3.app()
