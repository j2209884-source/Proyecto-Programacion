import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@st.cache_data
def leer_archivo(ruta):
    df = pd.read_csv(ruta)
    return df


def crear_graficos(df):

    st.header("Dashboard de Evolución del Agua en México (INEGI)")
    st.write("Indicadores de descargas, tomas y tratamiento del agua (2016–2020)")

    #-------------------------------------------
    #   FILTROS
    #-------------------------------------------
    st.sidebar.header("Filtros")

    estados = ["Todos"] + sorted(df["Estado"].unique())
    estado_sel = st.sidebar.selectbox("Selecciona un estado", estados)

    años = st.sidebar.slider(
        "Rango de años",
        min(df["Año"]),
        max(df["Año"]),
        (2016, 2020)
    )

    estado_linea = st.sidebar.selectbox(
        "Estado para línea individual",
        sorted(df["Estado"].unique())
    )

    df_f = df[(df["Año"] >= años[0]) & (df["Año"] <= años[1])]

    if estado_sel != "Todos":
        df_f = df_f[df_f["Estado"] == estado_sel]

    #-------------------------------------------
    #   KPIs
    #-------------------------------------------
    st.subheader("Indicadores Clave (2016 → 2020)")

    col1, col2, col3 = st.columns(3)

    df_2016 = df[df["Año"] == 2016]
    df_2020 = df[df["Año"] == 2020]

    # KPI 1
    d2016 = df_2016["descargas_municipales_sin_tratamiento"].sum()
    d2020 = df_2020["descargas_municipales_sin_tratamiento"].sum()
    col1.metric("% cambio descargas sin tratamiento", f"{((d2020 - d2016) / d2016) * 100:.2f}%")

    # KPI 2
    m2016 = df_2016["tomas_macromedidor_funcionando"].sum()
    m2020 = df_2020["tomas_macromedidor_funcionando"].sum()
    col2.metric("% cambio macromedidores funcionando", f"{((m2020 - m2016) / m2016) * 100:.2f}%")

    # KPI 3
    prom_nac = df["descargas_municipales_sin_tratamiento"].mean()
    prom_sel = df_f["descargas_municipales_sin_tratamiento"].mean()
    col3.metric("Promedio Nacional / Selección", f"{prom_nac:.1f} / {prom_sel:.1f}")

    #-------------------------------------------
    # VISUALIZACIONES
    #-------------------------------------------

    st.header("Visualizaciones Principales")

    st.subheader("Evolución nacional – tomas sin macromedidor")
    df_line1 = df.groupby("Año")["tomas_sin_macromedidor"].sum().reset_index()
    st.plotly_chart(px.line(df_line1, x="Año", y="tomas_sin_macromedidor", markers=True), use_container_width=True)

    st.subheader("Evolución nacional – tomas con macromedidor funcionando")
    df_line2 = df.groupby("Año")["tomas_macromedidor_funcionando"].sum().reset_index()
    st.plotly_chart(px.line(df_line2, x="Año", y="tomas_macromedidor_funcionando", markers=True), use_container_width=True)

    st.subheader("Evolución nacional – descargas municipales sin tratamiento")
    df_line3 = df.groupby("Año")["descargas_municipales_sin_tratamiento"].sum().reset_index()
    st.plotly_chart(px.line(df_line3, x="Año", y="descargas_municipales_sin_tratamiento", markers=True), use_container_width=True)

    st.subheader("Área apilada – Descargas sin tratamiento (Río, Mar, Lago)")
    df_area = df.groupby("Año")[
        ["descargas_sin_tratamiento_rio",
         "descargas_sin_tratamiento_mar",
         "descargas_sin_tratamiento_lago"]
    ].sum().reset_index()

    st.plotly_chart(px.area(df_area, x="Año", y=df_area.columns[1:]), use_container_width=True)

    st.subheader(f"Evolución de descargas municipales – {estado_linea}")
    df_st = df[df["Estado"] == estado_linea].groupby("Año")[
        "descargas_municipales_sin_tratamiento"
    ].sum().reset_index()

    st.plotly_chart(px.line(df_st, x="Año", y="descargas_municipales_sin_tratamiento", markers=True), use_container_width=True)

    st.subheader("Mapa de calor – Descargas sin tratamiento (Año vs Estado)")
    df_heat = df.pivot_table(
        index="Estado",
        columns="Año",
        values="descargas_municipales_sin_tratamiento",
        aggfunc="sum"
    )
    st.plotly_chart(px.imshow(df_heat, aspect="auto", color_continuous_scale="Reds"), use_container_width=True)

    st.subheader("Tomas públicas – comparación 2016 vs 2020")
    df_cmp = df[df["Año"].isin([2016, 2020])].groupby("Año")[
        "tomas_abastecimiento_publico"
    ].sum().reset_index()

    st.plotly_chart(px.bar(df_cmp, x="Año", y="tomas_abastecimiento_publico", text="tomas_abastecimiento_publico"), use_container_width=True)

    st.subheader("Datos filtrados")
    st.dataframe(df_f)


def app():
    st.set_page_config(page_title="Dashboard Evolución del Agua en México", layout="wide")
    st.title("Dashboard Evolución del Agua (2016–2020)")
    st.subheader("**Visualización dinámica por estado y año**")
    st.divider()

    df = leer_archivo("dataframes/datos_formato_ancho.csv")
    crear_graficos(df)

if __name__ == "__main__":
    app()