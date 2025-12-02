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

    # Grafico 2
    st.subheader("Descargas sin tratamiento (Mar)")
    fig_sin_tratamiento_mar = px.bar(df_filtrado, x="descargas_sin_tratamiento_mar",
                                     y="Estado", orientation="h", color="Estado",
                                     color_discrete_sequence=px.colors.qualitative.Set1,
                                     title=f"Descargas sin tratamiento en mar - Año {seleccionar_year}"
                                     )
    st.plotly_chart(fig_sin_tratamiento_mar)

    # Grafico 3
    st.subheader("Descargas sin tratamiento (Lago)")
    fig_sin_tratamiento_lago = px.bar(
        df_filtrado,
        x="descargas_sin_tratamiento_lago",
        y="Estado",
        orientation="h",
        color="Estado",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title=f"Descargas sin tratamiento en lago - Año {seleccionar_year}"
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
        title=f"Descargas totales sin tratamiento  - Año {seleccionar_year}",
    )
    fig_sin_tratamiento_total.update_layout(barmode="relative")  # ver de un color la distrubusion
    st.plotly_chart(fig_sin_tratamiento_total)

    # Gráfico 5
    st.subheader("Proporción de medidores funcionando (Nivel Nacional)")
    # suma a valores
    total_funcionando = df_filtrado["tomas_macromedidor_funcionando"].sum()
    total_descompuesto = df_filtrado["tomas_macromedidor_descompuesto"].sum()
    total_sin_macromedidor = df_filtrado["tomas_sin_macromedidor"].sum()
    total_no_funcionando = (total_descompuesto + total_sin_macromedidor)

    df_pie = pd.DataFrame(
        {"Categoria": ["Funcionando", "No Funcionando"], "Cantidad": [total_funcionando, total_no_funcionando]})

    fig_medidor_funcionando = px.pie(df_pie, names="Categoria", values="Cantidad", color="Categoria",
                                     color_discrete_sequence=px.colors.qualitative.Pastel,
                                     title=f"Medidores funcionando vs No funcionando en {seleccionar_year}")

    fig_medidor_funcionando.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_medidor_funcionando)

    # Grafico 6 Mapa
    # Source - https://stackoverflow.com/q
    # Posted by Moreno
    # Retrieved 2025-12-02, License - CC BY-SA 4.0

    data = {'estado': {0: 'oaxaca',
                       1: 'nuevo león',
                       2: 'guerrero',
                       3: 'hidalgo',
                       4: 'baja california sur',
                       5: 'puebla',
                       6: 'nayarit',
                       7: 'tabasco',
                       8: 'baja california',
                       9: 'quintana roo',
                       10: 'michoacan de ocampo',
                       11: 'tamaulipas',
                       12: 'veracruz de ignacio de la llave',
                       13: 'sinaloa',
                       14: 'colima',
                       15: 'ciudad de mexico',
                       16: 'morelos',
                       17: 'veracruz de ignacio',
                       18: 'chiapas',
                       19: 'mexico',
                       20: 'tlaxcala',
                       21: 'yucatan',
                       22: 'durango',
                       23: 'chihuahua',
                       24: 'zacatecas',
                       25: 'jalisco',
                       26: 'coahuila de zaragoza',
                       27: 'san luis potosi',
                       28: 'aguascalientes',
                       29: 'campeche',
                       30: 'nuevo leon',
                       31: 'queretaro',
                       32: 'guanajuato',
                       33: 'sonora'},
            'percentage': {0: 0.34558823529411764,
                           1: 0.3333333333333333,
                           2: 0.3218390804597701,
                           3: 0.30857142857142855,
                           4: 0.30120481927710846,
                           5: 0.28860294117647056,
                           6: 0.2857142857142857,
                           7: 0.2616033755274262,
                           8: 0.2576530612244898,
                           9: 0.2483221476510067,
                           10: 0.23902439024390243,
                           11: 0.23595505617977527,
                           12: 0.23383084577114427,
                           13: 0.2289855072463768,
                           14: 0.22727272727272727,
                           15: 0.22676579925650558,
                           16: 0.22330097087378642,
                           17: 0.22186495176848875,
                           18: 0.21978021978021978,
                           19: 0.2153928380545163,
                           20: 0.20689655172413793,
                           21: 0.1980952380952381,
                           22: 0.19626168224299065,
                           23: 0.19240506329113924,
                           24: 0.1875,
                           25: 0.1852576647097195,
                           26: 0.18493150684931506,
                           27: 0.18250950570342206,
                           28: 0.18064516129032257,
                           29: 0.18007662835249041,
                           30: 0.17862481315396114,
                           31: 0.1733490566037736,
                           32: 0.16173570019723865,
                           33: 0.15902140672782875}}

    mis_estados = df['estado'].unique()
    estados_otro = list(data['estado'].values())
    df_sorted= df.sort_values('estado')




    # Mostrar DataFrame
    st.subheader("Descargas sin tratamiento (Lago)")
    st.dataframe(df)

def app_stremalit(df):
    st.title("Dashboard Nacional del Agua en México (2016–2020)")
    st.markdown("**Análisis de indicadores de infraestructura hídrica por estado**")
    st.write("Visualizaras graficas")
    crear_graficos(df)




if __name__=="__main__":
    data = leer_archivo("datos_formato_ancho.csv")
    data= calculos(data)
    app_stremalit(data)

