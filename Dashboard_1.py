import pandas as pd
import streamlit as st
import plotly.express as px
import requests


def leer_archivo(ruta):
    df = pd.read_csv(ruta)
    return df


def crear_graficos(df):
    with st.container():
        # Seleccionar el tiempo para todos los graficos
        st.subheader("**📅 Selecciona el periodo de tiempo**")
        years = sorted(df['Año'].unique())

        years_opciones = ["Todos los años (2016-2020)", "2016", "2018", "2020"]
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
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

    with kpi1:
        # Total descargas sin tratamiento
        total_descargas = df_filtrado[
            ["descargas_sin_tratamiento_rio", "descargas_sin_tratamiento_mar",
             "descargas_sin_tratamiento_lago", "descargas_municipales_sin_tratamiento"]
        ].sum().sum()
        st.metric("Total Descargas", round(total_descargas))
    with kpi2:
        # Total tomas funcionand
        total_funcionando = df_filtrado["tomas_macromedidor_funcionando"].sum()
        st.metric("Tomas funcionando", round(total_funcionando))

    with kpi3:
        # Total tomas sin macromedidor
        total_sin = df_filtrado["tomas_sin_macromedidor"].sum()
        st.metric("Tomas sin macromedidor", round(total_sin))

    with kpi4:
        # % tomas funcionando
        total_no_funcionando = df_filtrado["tomas_macromedidor_descompuesto"].sum() + total_sin
        porcentaje_funcionando = total_funcionando / (total_funcionando + total_no_funcionando) * 100
        porcentaje_redondeado = round(porcentaje_funcionando)
        st.metric("% Tomas funcionando", f"{porcentaje_redondeado} %")

    st.divider()

    st.subheader("Descargas sin Tratamiento por Cuerpo de Agua")
    col1, col2 = st.columns(2, gap="large")  # Controla el espacio entre columnas
    with col1:
        # Gráfico 1
        st.subheader("Descargas sin Tratamiento (Río)")
        fig_sin_tratamiento_rio = px.bar(
            df_filtrado,
            x="descargas_sin_tratamiento_rio",
            y="Estado",
            orientation="h",
            color="Estado",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=600)
        fig_sin_tratamiento_rio.update_layout(
            xaxis_title="Cantidad de descargas",
            yaxis_title="Estado", showlegend=False)
        st.plotly_chart(fig_sin_tratamiento_rio, use_container_width=True)  # Expande el gráfico ancho columna

    with col2:
        # Gráfico 2
        st.subheader("Descargas sin Tratamiento (Mar)")
        fig_sin_tratamiento_mar = px.bar(
            df_filtrado,
            x="descargas_sin_tratamiento_mar",
            y="Estado",
            orientation="h",
            color="Estado",
            color_discrete_sequence=px.colors.qualitative.Set1,
            height=600)
        fig_sin_tratamiento_mar.update_layout(
            xaxis_title="Cantidad de descargas",
            yaxis_title="Estado", showlegend=False)
        st.plotly_chart(fig_sin_tratamiento_mar, use_container_width=True)

    col3, col4 = st.columns(2, gap="large")
    with col3:
        # Gráfico 3
        st.subheader("Descargas sin Tratamiento (Lago)")
        fig_sin_tratamiento_lago = px.bar(
            df_filtrado,
            x="descargas_sin_tratamiento_lago",
            y="Estado",
            orientation="h",
            color="Estado",
            color_discrete_sequence=px.colors.qualitative.Set2,
            height=600)
        fig_sin_tratamiento_lago.update_layout(
            xaxis_title="Cantidad de descargas",
            yaxis_title="Estado", showlegend=False)
        st.plotly_chart(fig_sin_tratamiento_lago, use_container_width=True)

    with col4:
        # Gráfico 4
        st.subheader("Descargas sin Tratamiento (Apiladas)")
        fig_sin_tratamiento_total = px.bar(
            df_filtrado,
            x="Estado",
            y=["descargas_sin_tratamiento_rio", "descargas_sin_tratamiento_mar", "descargas_sin_tratamiento_lago",
               "descargas_municipales_sin_tratamiento"],
            color_discrete_sequence=px.colors.qualitative.Bold,
            height=600)
        fig_sin_tratamiento_total.update_layout(
            barmode="relative",
            xaxis_title="Estado",
            yaxis_title="Cantidad de descargas")
        st.plotly_chart(fig_sin_tratamiento_total, use_container_width=True)

    st.divider()

    st.subheader("Análisis de Medidores y Tomas")
    col5, col6 = st.columns(2, gap="large")
    with col5:
        # Gráfico 5
        st.subheader("Proporción de Medidores Funcionando")
        total_funcionando = df_filtrado["tomas_macromedidor_funcionando"].sum()
        total_descompuesto = df_filtrado["tomas_macromedidor_descompuesto"].sum()
        total_sin_macromedidor = df_filtrado["tomas_sin_macromedidor"].sum()
        total_no_funcionando = total_descompuesto + total_sin_macromedidor

        df_pie = pd.DataFrame({
            "Categoria": ["Funcionando", "No Funcionando"],
            "Cantidad": [total_funcionando, total_no_funcionando]
        })

        fig_medidor_funcionando = px.pie(
            df_pie,
            names="Categoria",
            values="Cantidad",
            color="Categoria",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=600)

        fig_medidor_funcionando.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_medidor_funcionando, use_container_width=True)

    with col6:
        # Gráfico 6
        st.subheader("Mapa: % de Tomas sin Macromedidor")
        df_mapa = df_filtrado.groupby('Estado')['tomas_sin_macromedidor'].sum().reset_index()
        total_mapa = df_mapa['tomas_sin_macromedidor'].sum()
        df_mapa['percentage'] = df_mapa['tomas_sin_macromedidor'] / total_mapa
        df_mapa['Porcentaje'] = (df_mapa['percentage'] * 100).round(2).astype(str) + '%'

        geo_regiones = requests.get(
            'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json').json()

        fig_sin_macromedidor = px.choropleth(
            df_mapa,
            geojson=geo_regiones,
            locations='Estado',
            featureidkey='properties.name',
            color='percentage',
            color_continuous_scale="Reds",
            hover_name='Estado',
            hover_data={'percentage': False, 'Porcentaje': True},
            height=600)

        fig_sin_macromedidor.update_geos(fitbounds="locations", visible=True)
        fig_sin_macromedidor.update_geos(showcountries=True, showcoastlines=True, showland=True, fitbounds="locations")
        # fig_sin_macromedidor.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_sin_macromedidor, use_container_width=True)

    st.divider()

    col7, col8 = st.columns(2, gap="large")
    with col7:
        # Gráfico 7
        st.subheader("Top 10: Tomas con Macromedidor Funcionando")
        top10 = df_filtrado.nlargest(10, "tomas_macromedidor_funcionando")

        fig_top10_funcionando = px.bar(
            top10,
            x="tomas_macromedidor_funcionando",
            y="Estado",
            orientation="h",
            color="tomas_macromedidor_funcionando",
            color_continuous_scale="Blues",
            height=600)
        fig_top10_funcionando.update_layout(
            xaxis_title="Cantidad de Macromedidores Funcionando",
            yaxis_title="Estado",
            coloraxis_showscale=False)
        st.plotly_chart(fig_top10_funcionando, use_container_width=True)

    with col8:
        # Gráfico 8
        st.subheader("Relación: Tomas sin Medidor vs. Descargas Municipales")
        fig_relacion = px.scatter(
            df_filtrado,
            x="tomas_sin_macromedidor",
            y="descargas_municipales_sin_tratamiento",
            color="Estado",
            size="descargas_municipales_sin_tratamiento",
            color_discrete_sequence=px.colors.qualitative.Set1,
            height=600)
        fig_relacion.update_layout(xaxis_title="Cantidad de tomas sin macromedidor",
                                   yaxis_title="Descargas municipales sin tratamiento")
        st.plotly_chart(fig_relacion, use_container_width=True)


def app_streamlit():
    # Configuración página
    # lograr que los graficos ocupen toda la pagina y no solo esten en el centro
    st.set_page_config(page_title="Dashboard Nacional del Agua en México", layout="wide")
    st.title("💧 Dashboard Nacional del Agua en México (2016–2020)")
    st.subheader("**Análisis de indicadores de infraestructura hídrica por estado**")
    st.divider()

    # cargar datos
    df = leer_archivo("dataframes/datos_formato_ancho.csv")
    crear_graficos(df)


if __name__ == "__main__":
    app_streamlit()

import pandas as pd
import streamlit as st
import plotly.express as px
import requests


def leer_archivo(ruta):
    df = pd.read_csv(ruta)
    return df


def crear_graficos(df):
    with st.container():
        # Seleccionar el tiempo para todos los graficos
        st.subheader("**📅 Selecciona el periodo de tiempo**")
        years = sorted(df['Año'].unique())

        years_opciones = ["Todos los años (2016-2020)", "2016", "2018", "2020"]
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
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

    with kpi1:
        # Total descargas sin tratamiento
        total_descargas = df_filtrado[
            ["descargas_sin_tratamiento_rio", "descargas_sin_tratamiento_mar",
             "descargas_sin_tratamiento_lago", "descargas_municipales_sin_tratamiento"]
        ].sum().sum()
        st.metric("Total Descargas", round(total_descargas))
    with kpi2:
        # Total tomas funcionand
        total_funcionando = df_filtrado["tomas_macromedidor_funcionando"].sum()
        st.metric("Tomas funcionando", round(total_funcionando))

    with kpi3:
        # Total tomas sin macromedidor
        total_sin = df_filtrado["tomas_sin_macromedidor"].sum()
        st.metric("Tomas sin macromedidor", round(total_sin))

    with kpi4:
        # % tomas funcionando
        total_no_funcionando = df_filtrado["tomas_macromedidor_descompuesto"].sum() + total_sin
        porcentaje_funcionando = total_funcionando / (total_funcionando + total_no_funcionando) * 100
        porcentaje_redondeado = round(porcentaje_funcionando)
        st.metric("% Tomas funcionando", f"{porcentaje_redondeado} %")

    st.divider()

    st.subheader("Descargas sin Tratamiento por Cuerpo de Agua")
    col1, col2 = st.columns(2, gap="large")  # Controla el espacio entre columnas
    with col1:
        # Gráfico 1
        st.subheader("Descargas sin Tratamiento (Río)")
        fig_sin_tratamiento_rio = px.bar(
            df_filtrado,
            x="descargas_sin_tratamiento_rio",
            y="Estado",
            orientation="h",
            color="Estado",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=600)
        fig_sin_tratamiento_rio.update_layout(
            xaxis_title="Cantidad de descargas",
            yaxis_title="Estado", showlegend=False)
        st.plotly_chart(fig_sin_tratamiento_rio, use_container_width=True)  # Expande el gráfico ancho columna

    with col2:
        # Gráfico 2
        st.subheader("Descargas sin Tratamiento (Mar)")
        fig_sin_tratamiento_mar = px.bar(
            df_filtrado,
            x="descargas_sin_tratamiento_mar",
            y="Estado",
            orientation="h",
            color="Estado",
            color_discrete_sequence=px.colors.qualitative.Set1,
            height=600)
        fig_sin_tratamiento_mar.update_layout(
            xaxis_title="Cantidad de descargas",
            yaxis_title="Estado", showlegend=False)
        st.plotly_chart(fig_sin_tratamiento_mar, use_container_width=True)

    col3, col4 = st.columns(2, gap="large")
    with col3:
        # Gráfico 3
        st.subheader("Descargas sin Tratamiento (Lago)")
        fig_sin_tratamiento_lago = px.bar(
            df_filtrado,
            x="descargas_sin_tratamiento_lago",
            y="Estado",
            orientation="h",
            color="Estado",
            color_discrete_sequence=px.colors.qualitative.Set2,
            height=600)
        fig_sin_tratamiento_lago.update_layout(
            xaxis_title="Cantidad de descargas",
            yaxis_title="Estado", showlegend=False)
        st.plotly_chart(fig_sin_tratamiento_lago, use_container_width=True)

    with col4:
        # Gráfico 4
        st.subheader("Descargas sin Tratamiento (Apiladas)")
        fig_sin_tratamiento_total = px.bar(
            df_filtrado,
            x="Estado",
            y=["descargas_sin_tratamiento_rio", "descargas_sin_tratamiento_mar", "descargas_sin_tratamiento_lago",
               "descargas_municipales_sin_tratamiento"],
            color_discrete_sequence=px.colors.qualitative.Bold,
            height=600)
        fig_sin_tratamiento_total.update_layout(
            barmode="relative",
            xaxis_title="Estado",
            yaxis_title="Cantidad de descargas")
        st.plotly_chart(fig_sin_tratamiento_total, use_container_width=True)

    st.divider()

    st.subheader("Análisis de Medidores y Tomas")
    col5, col6 = st.columns(2, gap="large")
    with col5:
        # Gráfico 5
        st.subheader("Proporción de Medidores Funcionando")
        total_funcionando = df_filtrado["tomas_macromedidor_funcionando"].sum()
        total_descompuesto = df_filtrado["tomas_macromedidor_descompuesto"].sum()
        total_sin_macromedidor = df_filtrado["tomas_sin_macromedidor"].sum()
        total_no_funcionando = total_descompuesto + total_sin_macromedidor

        df_pie = pd.DataFrame({
            "Categoria": ["Funcionando", "No Funcionando"],
            "Cantidad": [total_funcionando, total_no_funcionando]
        })

        fig_medidor_funcionando = px.pie(
            df_pie,
            names="Categoria",
            values="Cantidad",
            color="Categoria",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=600)

        fig_medidor_funcionando.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_medidor_funcionando, use_container_width=True)

    with col6:
        # Gráfico 6
        st.subheader("Mapa: % de Tomas sin Macromedidor")
        df_mapa = df_filtrado.groupby('Estado')['tomas_sin_macromedidor'].sum().reset_index()
        total_mapa = df_mapa['tomas_sin_macromedidor'].sum()
        df_mapa['percentage'] = df_mapa['tomas_sin_macromedidor'] / total_mapa
        df_mapa['Porcentaje'] = (df_mapa['percentage'] * 100).round(2).astype(str) + '%'

        geo_regiones = requests.get(
            'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json').json()

        fig_sin_macromedidor = px.choropleth(
            df_mapa,
            geojson=geo_regiones,
            locations='Estado',
            featureidkey='properties.name',
            color='percentage',
            color_continuous_scale="Reds",
            hover_name='Estado',
            hover_data={'percentage': False, 'Porcentaje': True},
            height=600)

        fig_sin_macromedidor.update_geos(fitbounds="locations", visible=True)
        fig_sin_macromedidor.update_geos(showcountries=True, showcoastlines=True, showland=True, fitbounds="locations")
        # fig_sin_macromedidor.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_sin_macromedidor, use_container_width=True)

    st.divider()

    col7, col8 = st.columns(2, gap="large")
    with col7:
        # Gráfico 7
        st.subheader("Top 10: Tomas con Macromedidor Funcionando")
        top10 = df_filtrado.nlargest(10, "tomas_macromedidor_funcionando")

        fig_top10_funcionando = px.bar(
            top10,
            x="tomas_macromedidor_funcionando",
            y="Estado",
            orientation="h",
            color="tomas_macromedidor_funcionando",
            color_continuous_scale="Blues",
            height=600)
        fig_top10_funcionando.update_layout(
            xaxis_title="Cantidad de Macromedidores Funcionando",
            yaxis_title="Estado",
            coloraxis_showscale=False)
        st.plotly_chart(fig_top10_funcionando, use_container_width=True)

    with col8:
        # Gráfico 8
        st.subheader("Relación: Tomas sin Medidor vs. Descargas Municipales")
        fig_relacion = px.scatter(
            df_filtrado,
            x="tomas_sin_macromedidor",
            y="descargas_municipales_sin_tratamiento",
            color="Estado",
            size="descargas_municipales_sin_tratamiento",
            color_discrete_sequence=px.colors.qualitative.Set1,
            height=600)
        fig_relacion.update_layout(xaxis_title="Cantidad de tomas sin macromedidor",
                                   yaxis_title="Descargas municipales sin tratamiento")
        st.plotly_chart(fig_relacion, use_container_width=True)


def app_streamlit():
    # Configuración página
    # lograr que los graficos ocupen toda la pagina y no solo esten en el centro
    st.set_page_config(page_title="Dashboard Nacional del Agua en México", layout="wide")
    st.title("💧 Dashboard Nacional del Agua en México (2016–2020)")
    st.subheader("**Análisis de indicadores de infraestructura hídrica por estado**")
    st.divider()

    # cargar datos
    df = leer_archivo("dataframes/datos_formato_ancho.csv")
    crear_graficos(df)


if __name__ == "__main__":
    app_streamlit()

