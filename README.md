# Proyecto-Programacion

## Descripción
Este código descarga datos de indicadores de agua del INEGI para todos los estados de México, procesando las combinaciones de estado-indicador mediante solicitudes a la API. Con la información obtenida, se genera un DataFrame, limpia los datos y produce archivos CSV con formato largo y ancho para los dashboards realizados después.

El programa se conecta a una base de datos en MySQL (la cual se le debe cambiar USER y PASSWORD) e inserta catálogos de estados e indicadores si las tablas estan vacías. Para terminar, carga los datos limpios a la tabla principal en donde registra en año, estado, indicador y valor. Todo se ejecuta automáticamente al correr el script.

## Punto a tomar en cuenta
Se obtuvieron más de 700 datos a través de la API, sin embargo, para optimizar los dashboards, fue necesario transformar los datos a una estructura horizontal, mejorando así tanto la presentación visual como el manejo del código.

## Proceso para usarlo
1. Descargar el archivo .sql (MySQL) y ejecutarlo
2. Abrir los demás archivos (carpetas y .py) en PyCharm
3. Ejecutar primero el archivo "Extraccion y limpieza"
4. Ejecutar el archivo "app.py" para ver los dashboards
5. Y listo!! 😊

## Colaboradores
* Bernardino Martinez Itzel Karina (2209552) 
* Castillo González Ingrid Paola (2204086) 
* Meneses Valencia Marlen Alicia (2211138)  
* Ortiz Pérez Jennifer Anahi (2209884) 
* Pita Orozco Yamilet (2211129)
