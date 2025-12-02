import pandas as pd
import streamlit as st
import plotly.express as px

def leer_archivo(ruta):
    df= pd.read_csv(ruta)
    return df


def calculos(df):
    df["descargas_totales"]=(
            df["descargas_sin_tratamiento_rio"] +
            df["descargas_sin_tratamiento_mar"] +
            df["descargas_sin_tratamiento_lago"] +
            df["descargas_municipales_sin_tratamiento"] )

    return df

def crear_graficos(df):

    # filtrar por year
    years= sorted(df['Año'].unique())
    seleccionar_year= st.selectbox("Selecciona un año",years)
    df_filtrado= df[df["Año"] == seleccionar_year]

    # Grafico 1
    st.subheader("Descargas sin tratamiento (Río)")
    fig_sin_tratamiento_rio = px.bar(df_filtrado,x="descargas_sin_tratamiento_rio",y="Estado",orientation="h",title= f"Descargas sin tratamiento en río - Año {seleccionar_year})")
    st.plotly_chart(fig_sin_tratamiento_rio)



def app_stremalit(df):
    st.title("Dashboard Nacional del Agua en México (2016–2020)")
    st.markdown("**Análisis de indicadores de infraestructura hídrica por estado**")
    st.write("Visualizaras graficas")
    crear_graficos(df)




if __name__=="__main__":
    data = leer_archivo("datos_formato_ancho.csv")
    data= calculos(data)
    app_stremalit(data)

