
import streamlit as st

# Se traen los archivos de los dashbords que se van a utilizar
from pages import Dashboard_1,Dashboard_2,Dashboard_3

#nombramos  la pestaña del navegador
st.set_page_config(page_title="Proyecto Final", layout="wide")

st.title("🌎 Bienvenido al Proyecto Final")
st.sidebar.title("Navegación")


# Se crea un menu de opciones
page = st.sidebar.radio("Selecciona una página:", ["Inicio", "Dashboard 1", "Dashboard 2", "Dashboard 3"])


# opc menu
if page == "Inicio":
    st.markdown("### Bienvenida e instrucciones del proyecto")
    st.write(
        """
        Este proyecto descarga, limpia y transforma datos de indicadores del agua en México 
        utilizando la API del INEGI.  

        Después, los datos se cargan a MySQL y se usan para generar tres dashboards:

        **Dashboard 1:** Visión general de los indicadores.  
        **Dashboard 2:** Evolución de indicadores por estado.  
        **Dashboard 3:** Comparaciones y rankings a nivel nacional.  

        Para usar el proyecto:
        1. Ejecuta el archivo **Extraccion y limpieza.py** para obtener y preparar los datos.
        2. Ejecuta **app.py** para visualizar los dashboards.
        3. Navega por las secciones desde la barra lateral.

        ¡Listo! Puedes explorar, analizar y comparar los datos como quieras.
        """
    )
elif page == "Dashboard 1":
    Dashboard_1.app()
elif page == "Dashboard 2":
    Dashboard_2.app()
elif page == "Dashboard 3":
    Dashboard_3.app()
