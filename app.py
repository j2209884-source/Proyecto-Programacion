import streamlit as st

# Se traen los archivos de los dashbords que se van a utilizar
from pages import Dashboard_1,Dashboard_2,Dashboard_3

#nombramos  la pestaña del navegador
st.set_page_config(page_title="Proyecto Final", layout="wide")

st.title("🌎 Bienvenido al Proyecto Final")
st.sidebar.title("Navegación")


# Se crea un menu de opciones
page = st.sidebar.radio("Selecciona una página:", ["Inicio", "Dashboard 1", "Dashboard 2", "Dashboard 3"])


# Aqui son las opciones que estan en el menu
if page == "Inicio":
    st.markdown("Bienvenida e instrucciones...")
    st.write("")
elif page == "Dashboard 1":
    Dashboard_1.app()
elif page == "Dashboard 2":
    Dashboard_2.app()
elif page == "Dashboard 3":
    Dashboard_3.app()
