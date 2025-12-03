import requests
import pandas as pd
import time
from mysql.connector import connect, Error




estados = {
   "01": "Aguascalientes", "02": "Baja California", "03": "Baja California Sur",
   "04": "Campeche", "05": "Coahuila", "06": "Colima", "07": "Chiapas",
   "08": "Chihuahua", "09": "Ciudad de México", "10": "Durango", "11": "Guanajuato",
   "12": "Guerrero", "13": "Hidalgo", "14": "Jalisco", "15": "Estado de México",
   "16": "Michoacán", "17": "Morelos", "18": "Nayarit", "19": "Nuevo León",
   "20": "Oaxaca", "21": "Puebla", "22": "Querétaro", "23": "Quintana Roo",
   "24": "San Luis Potosí", "25": "Sinaloa", "26": "Sonora", "27": "Tabasco",
   "28": "Tamaulipas", "29": "Tlaxcala", "30": "Veracruz", "31": "Yucatán", "32": "Zacatecas"}


indicadores = {
   "6200089265": "tomas_sin_macromedidor",
   "6200089270": "tomas_macromedidor_descompuesto",
   "6200089271": "tomas_macromedidor_funcionando",
   "6200089278": "descargas_sin_tratamiento_rio",
   "6200089280": "descargas_sin_tratamiento_mar",
   "6200089281": "descargas_sin_tratamiento_lago",
   "6200093527": "descargas_municipales_sin_tratamiento",
   "6200093528": "tomas_abastecimiento_publico"}


def extraer_api(indicadores_map, estados_map):
  token = "3912b903-b86c-8f19-3be3-77c2d242e948"
  todas_filas = []


  for indicador in indicadores_map:
      for clave_estado, nombre_estado in estados_map.items():


          url = f"https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{indicador}/es/{clave_estado}/false/BISE/2.0/{token}?type=json"
          resp = requests.get(url)


          if resp.status_code == 200:
              data = resp.json()
              for serie in data["Series"]:
                  for obs in serie["OBSERVATIONS"]:
                      todas_filas.append({
                          "Indicador": indicador,
                          "Nombre_Indicador": indicadores_map[indicador],
                          "Año": obs["TIME_PERIOD"],
                          "Valor": obs["OBS_VALUE"],
                          "Estado": nombre_estado,
                          "Clave_Estado": clave_estado})
          else:
              print(f"Error {resp.status_code} al obtener datos de {nombre_estado} para indicador {indicador}")
          time.sleep(1)




  df = pd.DataFrame(todas_filas)
  df.to_csv("dataframes/DatosAPIs_sin_formato.csv", index=False)
  return df




def limpiar_datos(ruta_csv):
   df = pd.read_csv(ruta_csv)


   # Convertir columna a tipo entero
   df["Año"] = pd.to_numeric(df["Año"], errors="coerce").astype("Int64")
   df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").astype("Int64")
   df["Clave_Estado"] = pd.to_numeric(df["Clave_Estado"], errors="coerce").astype("Int64")


   # Reemplazar nulos
   df["Valor"] = df["Valor"].fillna(0)


   # Convertir columnas a texto
   df["Indicador"] = df["Indicador"].astype(str)
   df["Nombre_Indicador"] = df["Nombre_Indicador"].astype(str)
   df["Estado"] = df["Estado"].astype(str)


   #Filtrar datos entre 2015 y 2020
   df_filtrado = df[(df["Año"] >= 2015) & (df["Año"] <= 2020)].copy()


   # Orden correcto de columnas (formato largo)
   df_filtrado = df_filtrado[["Indicador", "Nombre_Indicador", "Año", "Estado", "Clave_Estado", "Valor"]]
   df_filtrado.to_csv("dataframes/datos_formato_largo.csv", index=False)


   # Reorganizar Columnas (Formato ancho)
   df_ancho = df_filtrado.pivot(index=["Estado", "Clave_Estado", "Año"],columns="Nombre_Indicador",values="Valor").reset_index()


   # Formato ancho en CSV para Dashboard
   df_ancho.to_csv("dataframes/datos_formato_ancho.csv", index=False)
   return df_filtrado






def conectar(): #PERMITE CONNECTARME A BASE DE DATOS
 try:
     dbConexion=connect(host="127.0.0.2", user="root", password="Dani.123", database="indicadores_agua_inegi")
     print("Conexión exitosa a la base de datos.")
     return dbConexion
     #host  que servidore te quieres conectar (se puede usar una ip), user:admin, root, database: a que base de datos te quieres conectar
 except Error as e:
     print("Error al conectar a la base de datos:", e)
     return None #HASTA ES SOLO HACER LA CONEXION CON LA BASE DE DATOS




def insertar_catalogos(conexion, indicadores_map, estados_map):
    cursor = conexion.cursor()


    """
    Validar que no dupliquen los Estados
    """

    cursor.execute("SELECT COUNT(*) FROM estados")

    cant_est = cursor.fetchone()[0]


    if cant_est > 0:
        print("La tabla ya tiene los Estados, no sera necesario insertarlos nuevamente <:")

    else:
        for id_est, nombre_est in estados_map.items():
            cursor.execute(
                "INSERT INTO estados(id_estado, nom_Est) VALUES (%s, %s)",
                (int(id_est, nombre_est))
            )
        print("Se insertaron los Estados")


    """
    Validar que no se dupliquen los indicadores
    """
    cursor.execute("SELECT COUNT(*) FROM indicadores")
    cant_ind = cursor.fetchone()[0]

    if cant_ind > 0:
        print("La tabla ya tiene los Indicadores")
    else:
        for id_ind, nombre in indicadores_map.items():
            cursor.execute(
                "INSERT INTO indicadores(id_indicador, nom_Ind) VALUES (%s, %s)",
                (int(id_ind), nombre)
            )
        print("Se insertaron los Indicadores")

    conexion.commit()
    cursor.close()


def insertar_datos(conexion, df):
    cursor = conexion.cursor()

    """
    Validacion por si ya hay registros
    """
    cursor.execute("SELECT COUNT(*) FROM datos")
    cantidad = cursor.fetchone()[0]

    if cantidad > 0:
        print("La tabla ya tiene los Datos")
        cursor.close()
        return

    """
    Insertar datos si la tabla está vacía
    """
    sql = "INSERT INTO datos(año, id_estado, valor, id_indicador) VALUES (%s, %s, %s, %s)"

    for indice, fila in df.iterrows():
        cursor.execute(sql, (
            int(fila["Año"]),
            int(fila["Clave_Estado"]),
            float(fila["Valor"]),
            int(fila["Indicador"])
        ))

    conexion.commit()
    cursor.close()
    print("Los Datos se han insertado")



if __name__ == "__main__":
  df_raw=extraer_api(indicadores,estados)
  df_limpio = limpiar_datos("dataframes/DatosAPIs_sin_formato.csv")
  conexion = conectar()
  if conexion:
      insertar_catalogos(conexion,indicadores,estados)
      insertar_datos(conexion, df_limpio)
      conexion.close()
