import streamlit as st
import pandas as pd
import plotly.express as px
import plotly
import requests
import json

# para que no se repita la lectura del archivo CSV
@st.cache_data
def leer_archivo(ruta):
    df = pd.read_csv(ruta)

    # Sumamos todos los tipos de descargas de agua sucia
    df["descargas_totales"] = (
        df["descargas_municipales_sin_tratamiento"] +
        df["descargas_sin_tratamiento_lago"] +
        df["descargas_sin_tratamiento_mar"] +
        df["descargas_sin_tratamiento_rio"]
    )


    # Sumamos todas las tomas de agua
    df["tomas_totales"] = (
        df["tomas_abastecimiento_publico"] +
        df["tomas_macromedidor_descompuesto"] +
        df["tomas_macromedidor_funcionando"] +
        df["tomas_sin_macromedidor"]
    )

    # Sumamos las tomas que tienen problemas
    df["tomas_sin_medidor"] = (
        df["tomas_macromedidor_descompuesto"] +
        df["tomas_sin_macromedidor"]
    )

    return df


def crear_graficos(df):

    st.title("Evaluación de Riesgo Hídrico en México")
    st.write("Análisis avanzado basado en descargas y tomas de agua.")

    # ------------------------------
    # FILTROS
    # ------------------------------
    st.sidebar.header("Filtros")


    # Para elegir estado
    estado_sel = st.sidebar.selectbox(
        "Selecciona un estado",
        ["Todos"] + sorted(df["Estado"].unique())
    )

    años = st.sidebar.slider(
        "Rango de años",
        int(df["Año"].min()),
        int(df["Año"].max()),
        (2016, 2020)
    )

    indicadores = [
        "descargas_municipales_sin_tratamiento",
        "descargas_sin_tratamiento_lago",
        "descargas_sin_tratamiento_mar",
        "descargas_sin_tratamiento_rio",
        "descargas_totales",
        "tomas_abastecimiento_publico",
        "tomas_macromedidor_descompuesto",
        "tomas_macromedidor_funcionando",
        "tomas_sin_macromedidor",
        "tomas_sin_medidor",
        "tomas_totales"
    ]

    st.sidebar.write("### Indicadores a incluir:")
    indicadores_sel = []

    # Seleccionar casilla para indicadores
    for ind in indicadores:
        if st.sidebar.checkbox(ind, value=True):
            indicadores_sel.append(ind)

    # Si no hay seleccion, una advertencia
    if len(indicadores_sel) == 0:
        st.warning("Selecciona al menos un indicador.")
        st.stop()

    # APLICAR FILTROS
    df_f = df.copy()

    if estado_sel != "Todos":
        df_f = df_f[df_f["Estado"] == estado_sel]

    df_f = df_f[(df_f["Año"] >= años[0]) & (df_f["Año"] <= años[1])]

    # 1) Grafica 1:  MAPA DE RIESGO
    st.subheader("Mapa de Riesgo — Descargas sin tratamiento / Tomas totales")

    df_f["descargas_sin_tratamiento_totales"] = (
        df_f["descargas_municipales_sin_tratamiento"] +
        df_f["descargas_sin_tratamiento_lago"] +
        df_f["descargas_sin_tratamiento_mar"] +
        df_f["descargas_sin_tratamiento_rio"]
    )

    df_f["tomas_totales"] = (
        df_f["tomas_abastecimiento_publico"] +
        df_f["tomas_macromedidor_descompuesto"] +
        df_f["tomas_macromedidor_funcionando"] +
        df_f["tomas_sin_macromedidor"]
    )

    # Agrupacion
    df_riesgo = df_f.groupby("Estado").agg({
        "descargas_totales": "sum",
        "tomas_totales": "sum"
    }).reset_index()

    # Calculo para descargas entre tomas
    df_riesgo["riesgo"] = (
        df_riesgo["descargas_totales"] / df_riesgo["tomas_totales"]
    ).replace([float("inf"), -float("inf")], 0)

    # Descargar mapa de Mexico por internet
    url_geojson = "https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json"
    geojson_mex = requests.get(url_geojson).json()

    # Representacion del riesgo en el mapa
    fig_riesgo = px.choropleth(
        df_riesgo,
        geojson=geojson_mex,
        locations="Estado",
        featureidkey="properties.name",
        color="riesgo",
        color_continuous_scale="RdYlGn_r",
        title="Mapa de Riesgo Hídrico"
    )
    fig_riesgo.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_riesgo, use_container_width=True)

    # 2) Grafica 2: Scatter
    st.subheader("Ineficiencia — Tomas sin medidor vs. Medidores descompuestos")

    fig_scatter = px.scatter(
        df_f,
        x="descargas_sin_tratamiento_totales",
        y="tomas_totales",
        color="Estado"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


    # 3) Grafica 3: Pareto
    st.subheader("Pareto — Estados con más descargas sin tratamiento")

    df_pareto = df_riesgo.sort_values("descargas_totales", ascending=False)
    df_pareto["acumulado"] = df_pareto["descargas_totales"].cumsum()
    df_pareto["porcentaje"] = 100 * df_pareto["acumulado"] / df_pareto["descargas_totales"].sum()

    fig_pareto = px.bar(
        df_pareto,
        x="Estado",
        y="descargas_totales",
        title="Pareto de descargas sin tratamiento"
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # 4) Grafica 4: Correlaciones
    st.subheader("Matriz de correlaciones entre indicadores seleccionados")

    corr = df_f[indicadores_sel].corr()

    fig_corr = px.imshow(
        corr,
        text_auto=True,
        title="Heatmap de correlaciones"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # 5) Grafica 5:  Piechart
    st.subheader("Proporción nacional de tipos de descarga")

    df_pie = df_f[[
        "descargas_municipales_sin_tratamiento",
        "descargas_sin_tratamiento_lago",
        "descargas_sin_tratamiento_mar",
        "descargas_sin_tratamiento_rio"
    ]].sum().reset_index()

    df_pie.columns = ["Tipo", "Valor"]

    fig_pie = px.pie(df_pie, names="Tipo", values="Valor")
    st.plotly_chart(fig_pie, use_container_width=True)

    # 6) Grafica: Boxplot
    st.subheader("Distribución nacional (Boxplot)")

    df_box_long = df_f[indicadores_sel].melt(var_name="Indicador", value_name="Valor")

    fig_box = px.box(df_box_long, x="Indicador", y="Valor")
    st.plotly_chart(fig_box, use_container_width=True)

    # 7) Grafica 7: 100% Stacked
    st.subheader("Estructura de descargas por estado (100% Stacked)")

    df_stack = df_f.groupby("Estado")[
        [
            "descargas_municipales_sin_tratamiento",
            "descargas_sin_tratamiento_lago",
            "descargas_sin_tratamiento_mar",
            "descargas_sin_tratamiento_rio"
        ]
    ].sum().reset_index()

    fig_stack = px.bar(
        df_stack,
        x="Estado",
        y=[
            "descargas_municipales_sin_tratamiento",
            "descargas_sin_tratamiento_lago",
            "descargas_sin_tratamiento_mar",
            "descargas_sin_tratamiento_rio"
        ],
        barmode="relative"
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    # 8) Grafica 8: Bubble chart
    st.subheader("Bubble Chart — Prioridades por estado")

    df_bubble = df_f.groupby("Estado").agg({
        "tomas_sin_medidor": "sum",
        "tomas_abastecimiento_publico": "sum",
        "descargas_totales": "sum"
    }).reset_index()

    fig_bubble = px.scatter(
        df_bubble,
        x="tomas_sin_medidor",
        y="tomas_abastecimiento_publico",
        size="descargas_totales",
        color="Estado"
    )
    st.plotly_chart(fig_bubble, use_container_width=True)


    # 9) Tabla Recomendacion automatica
    st.subheader("Recomendación automática según riesgo")

    df_rec = df_riesgo.copy()

    df_rec["nivel_riesgo"] = pd.qcut(
        df_rec["riesgo"],
        q=4,
        labels=["Bajo", "Medio", "Alto", "Crítico"]
    )

    st.dataframe(df_rec)

def app():
    st.set_page_config(page_title="Evaluación de Riesgo Hídrico", layout="wide")
    st.title("Evaluación de Riesgo Hídrico en México")
    st.subheader("Dashboard basado en patrones de descarga y tomas de agua")
    st.divider()

    # cargar datos
    df = leer_archivo("dataframes/datos_formato_ancho.csv")
    crear_graficos(df)


if __name__ == "__main__":
    app()

