import pandas as pd
import streamlit as st
import plotly.express as px
import requests


def leer_archivo(ruta):
    df = pd.read_csv(ruta)
    return df


def crear_graficos(df):
    """Seleccionar el tiempo para todos los graficos """
    st.markdown("📅 Selecciona el periodo de tiempo")
    years = sorted(df['Año'].unique())

    years_opciones = ["Todos los años (2016-2020)", "2016","2018","2020"]
    seleccion = st.selectbox("Periodo para visualizar gráficos:", years_opciones)

    if seleccion == "Todos los años (2016-2020)":
        df_filtrado = df.groupby('Estado').sum().reset_index()
        titulo_year = "Todos los años (2016-2020)"
    else:
        year = int(seleccion)
        df_filtrado = df[df["Año"] == year]
        titulo_year = f"Año {year}"

    st.divider()

    # Indicadores (KPIs)
    st.subheader("Indicadores (KPIs)")
    col1, col2, col3, col4 = st.columns(4)

    # Total descargas sin tratamiento
    total_descargas = df_filtrado[
        ["descargas_sin_tratamiento_rio", "descargas_sin_tratamiento_mar",
         "descargas_sin_tratamiento_lago", "descargas_municipales_sin_tratamiento"]
    ].sum().sum()
    col1.metric("Total Descargas", round(total_descargas))

    # Total tomas funcionando
    total_funcionando = df_filtrado["tomas_macromedidor_funcionando"].sum()
    col2.metric("Tomas funcionando", round(total_funcionando))

    # Total tomas sin macromedidor
    total_sin = df_filtrado["tomas_sin_macromedidor"].sum()
    col3.metric("Tomas sin macromedidor", round(total_sin))

    # % tomas funcionando
    total_no_funcionando = df_filtrado["tomas_macromedidor_descompuesto"].sum() + total_sin
    porcentaje_funcionando = total_funcionando / (total_funcionando + total_no_funcionando) * 100
    porcentaje_redondeado = round(porcentaje_funcionando)
    col4.metric("% Tomas funcionando", f"{porcentaje_redondeado} %")

    st.divider()

    # Gráfico 1
    st.subheader("Descargas sin tratamiento (Río)")
    fig_sin_tratamiento_rio = px.bar(
        df_filtrado,
        x="descargas_sin_tratamiento_rio",
        y="Estado",
        orientation="h",
        color="Estado",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="Descargas sin tratamiento en río"
    )
    fig_sin_tratamiento_rio.update_layout(
        xaxis_title="Cantidad de descargas",
        yaxis_title="Estado",
    )
    st.plotly_chart(fig_sin_tratamiento_rio)

    # Gráfico 2
    st.subheader("Descargas sin tratamiento (Mar)")
    fig_sin_tratamiento_mar = px.bar(
        df_filtrado,
        x="descargas_sin_tratamiento_mar",
        y="Estado",
        orientation="h",
        color="Estado",
        color_discrete_sequence=px.colors.qualitative.Set1,
        title="Descargas sin tratamiento en mar"
    )
    fig_sin_tratamiento_mar.update_layout(
        xaxis_title="Cantidad de descargas",
        yaxis_title="Estado",
    )
    st.plotly_chart(fig_sin_tratamiento_mar)

    # Gráfico 3
    st.subheader("Descargas sin tratamiento (Lago)")
    fig_sin_tratamiento_lago = px.bar(
        df_filtrado,
        x="descargas_sin_tratamiento_lago",
        y="Estado",
        orientation="h",
        color="Estado",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Descargas sin tratamiento en lago"
    )
    fig_sin_tratamiento_lago.update_layout(
        xaxis_title="Cantidad de descargas",
        yaxis_title="Estado",
    )
    st.plotly_chart(fig_sin_tratamiento_lago)

    # Grafico 4
    st.subheader("Descargas sin tratamiento (Apiladas)")
    fig_sin_tratamiento_total = px.bar(
        df_filtrado,
        x="Estado",
        y=[
            "descargas_sin_tratamiento_rio",
            "descargas_sin_tratamiento_mar",
            "descargas_sin_tratamiento_lago",
            "descargas_municipales_sin_tratamiento",
        ],
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="Descargas totales sin tratamiento",
    )
    fig_sin_tratamiento_total.update_layout(
        barmode="relative",
        xaxis_title="Estado",
        yaxis_title="Cantidad de descargas",
    )
    st.plotly_chart(fig_sin_tratamiento_total)

    # Gráfico 5
    total_funcionando = df_filtrado["tomas_macromedidor_funcionando"].sum()
    total_descompuesto = df_filtrado["tomas_macromedidor_descompuesto"].sum()
    total_sin_macromedidor = df_filtrado["tomas_sin_macromedidor"].sum()
    total_no_funcionando = total_descompuesto + total_sin_macromedidor

    df_pie = pd.DataFrame({
        "Categoria": ["Funcionando", "No Funcionando"],
        "Cantidad": [total_funcionando, total_no_funcionando]
    })

    st.subheader("Proporción de medidores funcionando (Nivel Nacional)")
    fig_medidor_funcionando = px.pie(
        df_pie,
        names="Categoria",
        values="Cantidad",
        color="Categoria",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="Medidores funcionando vs No funcionando"
    )
    fig_medidor_funcionando.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_medidor_funcionando)

    # Gráfico 6
    st.subheader("Mapa del % de tomas sin macromedidor en México")
    df_mapa = df_filtrado.groupby('Estado')['tomas_sin_macromedidor'].sum().reset_index()
    total_mapa = df_mapa['tomas_sin_macromedidor'].sum()
    df_mapa['percentage'] = df_mapa['tomas_sin_macromedidor'] / total_mapa
    df_mapa['Porcentaje'] = (df_mapa['percentage'] * 100).round(2).astype(str) + '%'

    geo_regiones = requests.get('https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json').json()

    fig_sin_macromedidor = px.choropleth(
        df_mapa,
        geojson=geo_regiones,
        locations='Estado',
        featureidkey='properties.name',
        color='percentage',
        color_continuous_scale="Reds",
        hover_name='Estado',
        hover_data={'percentage': False, 'Porcentaje': True},
        title="Porcentaje de tomas sin macromedidor por estado"
    )
    fig_sin_macromedidor.update_geos(fitbounds="locations", visible=True)

    fig_sin_macromedidor.update_geos(showcountries=True, showcoastlines=True, showland=True, fitbounds="locations")

    st.plotly_chart(fig_sin_macromedidor)

    # Gráfico 7
    st.subheader("Top 10: Tomas con macromedidor funcionando")
    top10 = df_filtrado.nlargest(10, "tomas_macromedidor_funcionando")

    fig_top10_funcionando = px.bar(
        top10,
        x="tomas_macromedidor_funcionando",
        y="Estado",
        orientation="h",
        color_discrete_sequence=["#2E86AB"],
        title="Top 10 estados con más macromedidores funcionando"
    )
    fig_top10_funcionando.update_layout(
        xaxis_title="Cantidad de Macromedidores Funcionando",
        yaxis_title="Estado",)
    st.plotly_chart(fig_top10_funcionando)


    # Gráfico 8
    st.subheader("Relación: Tomas sin medidor vs. Descargas municipales sin tratamiento")

    # Crear scatter plot
    fig_relacion = px.scatter(
        df_filtrado,
        x="tomas_sin_macromedidor",
        y="descargas_municipales_sin_tratamiento",
        color="Estado",
        color_discrete_sequence=px.colors.qualitative.Set1,
        title="Relación entre tomas sin medidor y descargas municipales"
    )
    fig_relacion.update_layout(
        xaxis_title="Cantidad de tomas sin macromedidor",
        yaxis_title="Descargas municipales sin tratamiento")
    st.plotly_chart(fig_relacion)


def app_stremalit(df):
    st.title("Dashboard Nacional del Agua en México (2016–2020)")
    st.markdown("**Análisis de indicadores de infraestructura hídrica por estado**")
    crear_graficos(df)


if __name__ == "__main__":
    data = leer_archivo("datos_formato_ancho.csv")
    app_stremalit(data)