import plotly
import requests
import json
import streamlit as st
import pandas as pd
import plotly.express as px




@st.cache_data
def cargar_datos():
    df = pd.read_csv("dataframes/datos_formato_ancho.csv")
    return df

def dashboard(df):

    st.title("Dashboard de Evolución del Agua en México (INEGI)")
    st.write("Indicadores relacionados con descargas de agua sin tratar")

    # Lista de indicadores (todas las columnas excepto estas)
    columnas_fijas = ["Estado", "Clave_Estado", "Año"]
    indicadores = [c for c in df.columns if c not in columnas_fijas]

    # ------------------------------------
    # FILTROS
    # ------------------------------------
    st.sidebar.header("Filtros")

    # 1) Selector de Estado
    estado_sel = st.sidebar.selectbox(
        "Selecciona un estado",
        ["Todos"] + sorted(df["Estado"].unique())
    )

    # 2) Selector de Indicadores
    st.sidebar.write("### Indicadores disponibles:")

    lista_indicadores = [
        "descargas_municipales_sin_tratamiento",
        "descargas_sin_tratamiento_lago",
        "descargas_sin_tratamiento_mar",
        "descargas_sin_tratamiento_rio"
    ]

    indicadores_sel = []

    for ind in lista_indicadores:
        if st.sidebar.checkbox(ind, value=True):
            indicadores_sel.append(ind)

    # Evitar error si no seleccionan ninguno
    if len(indicadores_sel) == 0:
        st.warning("Selecciona al menos un indicador para visualizar datos.")
        st.stop()

    # 3) Filtro de años
    años = st.sidebar.slider(
        "Rango de años",
        int(df["Año"].min()),
        int(df["Año"].max()),
        (2016, 2020)
    )

    # Aplicar filtros al dataframe
    df_f = df.copy()

    # Filtrar por estado si no es "Todos"
    if estado_sel != "Todos":
        df_f = df_f[df_f["Estado"] == estado_sel]

    # Filtrar años
    df_f = df_f[(df_f["Año"] >= años[0]) & (df_f["Año"] <= años[1])]

    # ------------------------------------
    # MÉTRICAS CLAVE
    # ------------------------------------
    st.subheader("  Métricas Clave")

    col2, col3, col4 = st.columns(3)

    # Indicadores seleccionados
    indic_cols = indicadores_sel


    # METRICA 2: % variación 2016 → 2020
    df_2016 = df[df["Año"] == 2016][indic_cols].sum()
    df_2020 = df[df["Año"] == 2020][indic_cols].sum()
    variacion = ((df_2020.sum() - df_2016.sum()) / df_2016.sum()) * 100
    col2.metric("% Variación 2016 → 2020", f"{variacion:.2f}%")

    # MÉTRICA 3: Estado con mayor reducción / incremento
    df_estados = df.groupby("Estado")[indic_cols].sum().sum(axis=1)
    estado_max = df_estados.idxmax()
    estado_min = df_estados.idxmin()

    col3.metric("Mayor incremento", estado_max)
    col4.metric("Mayor reducción", estado_min)

    # ------------------------------------
    # PROMEDIO NACIONAL VS ESTADOS SELECCIONADOS
    # ------------------------------------
    promedio_nacional = df[indic_cols].mean().mean()
    promedio_estados = df_f[indic_cols].mean().mean()

    st.metric(
        "Promedio Nacional vs Estados Seleccionados",
        f"Nacional: {promedio_nacional:.2f} | Seleccionados: {promedio_estados:.2f}"
    )

    # ------------------------------------
    # GRÁFICA PRINCIPAL - LÍNEAS
    # ------------------------------------
    st.subheader("Evolución de los indicadores seleccionados")
    df_long = df_f.melt(
        id_vars=["Estado", "Año"],
        value_vars=indicadores_sel,
        var_name="Indicador",
        value_name="Valor"
    )

    fig = plotly.express.line(
        df_long,
        x="Año",
        y="Valor",
        color="Indicador",
        markers=True,
        title="Tendencia histórica"
    )

    st.plotly_chart(fig, use_container_width=True)

    # GRAFICA DE BARRAS
    st.subheader("Comparación entre estados")

    fig2 = plotly.express.bar(
        df_long,
        x="Estado",
        y="Valor",
        color="Indicador",
        barmode="group",
        title="Comparación por Estado"
    )

    st.plotly_chart(fig2, use_container_width=True)
    # -------------------------------------------------------------
    # HEATMAP POR ESTADO (USANDO URL)
    # -------------------------------------------------------------
    st.subheader("Mapa de Intensidad de Descargas sin Tratamiento")

    # Sumar los indicadores seleccionados por estado
    df_mapa = df_f.groupby("Estado")[indicadores_sel].sum().sum(axis=1).reset_index()
    df_mapa.columns = ["Estado", "Total_Descargas"]

    # Cargar GeoJSON
    url_geojson = "https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json"
    geojson_mex = requests.get(url_geojson).json()

    # Crear mapa
    fig_mapa = plotly.express.choropleth(
        df_mapa,
        geojson=geojson_mex,
        locations="Estado",
        featureidkey="properties.name",
        color="Total_Descargas",
        color_continuous_scale="Reds",
        title="Intensidad de descargas sin tratamiento por estado"
    )

    fig_mapa.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_mapa, use_container_width=True)

    # -------------------------------------------------------------
    # 2) RANKING DE ESTADOS
    st.subheader("Ranking de estados con más descargas sin tratamiento")

    df_rank = df_f.groupby("Estado")[indicadores_sel].sum().sum(axis=1).reset_index()
    df_rank.columns = ["Estado", "Total"]

    df_rank = df_rank.sort_values("Total", ascending=False)

    fig_rank = plotly.express.bar(
        df_rank,
        x="Estado",
        y="Total",
        title="Ranking de estados con mayores descargas sin tratamiento",
        text="Total"
    )

    fig_rank.update_traces(textposition="outside")
    st.plotly_chart(fig_rank, use_container_width=True)

    # -------------------------------------------------------------
    # 3) COMPOSICIÓN POR ESTADO
    # -------------------------------------------------------------
    st.subheader("Composición de descargas por estado")

    # Agrupar por estado solo los indicadores seleccionados
    df_stack = df_f.groupby("Estado")[indicadores_sel].sum().reset_index()

    df_stack_long = df_stack.melt(
        id_vars="Estado",
        value_vars=indicadores_sel,
        var_name="Tipo_descarga",
        value_name="Valor"
    )

    fig_stack = plotly.express.bar(
        df_stack_long,
        x="Estado",
        y="Valor",
        color="Tipo_descarga",
        title="Composición de descargas (río, lago, mar, municipales) por estado",
        barmode="stack"
    )

    st.plotly_chart(fig_stack, use_container_width=True)

    # TABLA FILTRADA
    st.subheader("Datos filtrados")
    st.dataframe(df_f)

if __name__=="__main__":
    df_d = cargar_datos()
    dashboard(df_d)