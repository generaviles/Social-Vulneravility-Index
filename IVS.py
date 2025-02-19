"""
06 feb 2025

Determinar el índice de vulnerabilidad social a nivel de manzana ante la amenaza de inundaciones por cambio climático, asociado a su clave geográfica. El propósito es identificar las áreas con mayor riesgo de inundación en la región de Presa La Villita, Michoacán de Ocampo.

Se establecerá una clasificación de vulnerabilidad en las siguientes categorías:

- Muy baja
- Baja
- Media
- Buena
- Muy buena

El cálculo del índice se realizará utilizando datos abiertos del Censo de Población y Vivienda 2020 del INEGI, específicamente de las Áreas Geoestadísticas Básicas (AGEB) de Michoacán de Ocampo.
"""

# Nota: En este ejercicio se generan distintos DataFrame para cada paso

# Selección e Importación de Datos 
# -------------------------------------------------------

import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Crear una ventana oculta de Tkinter
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Abrir el cuadro de diálogo para seleccionar el archivo
file_path = filedialog.askopenfilename(
    title="Selecciona un archivo CSV",
    filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
)
# Cargar el archivo CSV en un DataFrame (si se seleccionó un archivo)
if file_path:
    df = pd.read_csv(file_path)
    print("Archivo cargado con éxito")
    # print(df.head())  # Muestra las primeras filas
else:
    print("No se seleccionó ningún archivo")

# Ruta de guardado de archivos 
# -------------------------------------------------------

from tkinter import simpledialog

# Crear una ventana oculta de Tkinter
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Seleccionar ubicación
base_path = filedialog.askdirectory(title="Selecciona la ubicación donde crear la carpeta de destino")

if base_path:
    # Pedir nombre de la carpeta
    folder_name = simpledialog.askstring("Nombre de Carpeta", "Ingresa el nombre de la carpeta:")

    if folder_name:  
        # Crear la ruta completa
        folder_path = os.path.join(base_path, folder_name)

        # Crear la carpeta si no existe
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Carpeta creada en: {folder_path}")
        else:
            print(f"La carpeta ya existe: {folder_path}")

    else:
        print("No se ingresó un nombre de carpeta.")
else:
    print("No se seleccionó una ubicación base.")

# Generación de la clave geoestadística 
# --------------------------------------------------------

# Ajustar las claves a 16 dígitos, completando con ceros a la izquierda si es necesario.
# En este caso:
# 'ENTIDAD' se formatea a 2 dígitos.
# 'MUN' a 3 dígitos.
# 'AGEB' a 4 dígitos.
# 'LOC' a 4 dígitos.
# 'MZA' a 3 dígitos.

df['ENTIDAD'] = df['ENTIDAD'].astype(str).str.zfill(2)  # 2 dígitos
df['MUN'] = df['MUN'].astype(str).str.zfill(3)          # 3 dígitos
df['AGEB'] = df['AGEB'].astype(str).str.zfill(4)        # 4 dígitos
df['LOC'] = df['LOC'].astype(str).str.zfill(4)          # 4 dígitos
df['MZA'] = df['MZA'].astype(str).str.zfill(3)          # 3 dígitos

# Crear la nueva columna 'CVEGEO' (clave geoestadística) uniendo las claves modificadas 
# en el siguiente orden: ENTIDAD + MUN + LOC + AGEB + MZA

df['CVEGEO'] = df['ENTIDAD'] + df['MUN'] + df['LOC'] + df['AGEB'] + df['MZA']

# Insertar la nueva columna 'CVEGEO' inmediatamente después de la columna 'MZA'
col_index = df.columns.get_loc('MZA') + 1  # Obtener la posición después de 'MZA'
df.insert(col_index, 'CVEGEO', df.pop('CVEGEO'))

# Verificar las primeras filas de las columnas
print(df[['ENTIDAD', 'MUN', 'AGEB', 'LOC', 'MZA', 'CVEGEO']].head())

# Filtrado 
# ---------------------------------------------------------

# Eliminar filas donde la columna 'NOM_LOC' comienza con "Total" (resúmenes generales)
df_filtrado = df[~df["NOM_LOC"].astype(str).str.startswith("Total")].copy()

# Mostrar las primeras filas después del filtrado
print(df_filtrado.head(5))
# Número de filas restantes después del filtrado
print(f"Total de filas después del filtrado: {df_filtrado.shape[0]}")

# Depuración 
# --------------------------------------------------------

# Filtrar solo las columnas especificadas para el análisis
columnas_permitidas = [
    "CVEGEO", "POBTOT", "PROM_OCUP", "P3YM_HLI", "PHOGJEF_F", "P15YM_AN", 
    "GRAPROES", "PSINDER", "PEA", "POB15_64", "TVIVHAB", "VPH_AGUAFV", 
    "VPH_NODREN", "VPH_PISOTI"
]
# Aplicar la selección de columnas
df_depurado = df_filtrado[columnas_permitidas]

# Mostrar las primeras filas después del filtrado con las columnas seleccionadas
print(df_depurado.head(10))

# Conversión de columnas a valores númericos 
# --------------------------------------------------------

# Convertir todas las columnas a numéricas excepto 'CVEGEO'
df_depurado_num = df_depurado.drop(columns=['CVEGEO']).apply(pd.to_numeric, errors='coerce')

# Reagregar la columna 'CVEGEO' al DataFrame sin modificarla
df_depurado_num['CVEGEO'] = df_depurado['CVEGEO']

print(df_depurado_num.head(10))

# Contar los valores NaN en todo el DataFrame
nan_count = df_depurado_num.isna().sum().sum()
# Imprimir el número total de NaN
print(f'Número total de valores NaN: {nan_count}')

# Cálculo de Porcentajes por Categoría 
#--------------------------------------------------------

# Declarar df_porcentaje_categoria como un DataFrame vacío
df_porcentaje_categoria = pd.DataFrame()

# Integración de Columnas No Porcentuales en el DataFrame de Porcentaje de Categorías
df_porcentaje_categoria['CVEGEO'] = df_depurado_num['CVEGEO']  # 'CVEGEO' es la clave geografica
df_porcentaje_categoria['PROM_OCUP'] = df_depurado_num['PROM_OCUP']  # 'PROM_OCUP' ya viene en porcentajes
df_porcentaje_categoria['GRAPROES'] = df_depurado_num['GRAPROES']  # 'GRAPROES' ya viene en porcentajes

# Población
# La columna PROM_OCUP ya esta en porcentaje
df_porcentaje_categoria["P3YM_HLI_Perc_Nuevo"] = df_depurado_num["P3YM_HLI"] * 100 / df_depurado_num["POBTOT"]
df_porcentaje_categoria["PHOGJEF_F_Perc_Nuevo"] = df_depurado_num["PHOGJEF_F"] * 100 / df_depurado_num["POBTOT"]

# Educación
df_porcentaje_categoria["P15YM_AN_Perc_Nuevo"] = df_depurado_num["P15YM_AN"] * 100 / df_depurado_num["POBTOT"]
# La columna GRAPROES ya esta en porcentaje

# Salud
df_porcentaje_categoria["PSINDER_Perc_Nuevo"] = df_depurado_num["PSINDER"] * 100 / df_depurado_num["POBTOT"]

# Empleo
df_porcentaje_categoria["PEA_Perc_Nuevo"] = df_depurado_num["PEA"] * 100 / df_depurado_num["POBTOT"]
df_porcentaje_categoria["POB15_64_Perc_Nuevo"] = (df_depurado_num["POBTOT"] - df_depurado_num["POB15_64"]) * 100 / df_depurado_num["POBTOT"]

# Vivienda
df_porcentaje_categoria["VPH_AGUAFV_Perc_Nuevo"] = df_depurado_num["VPH_AGUAFV"] * 100 / df_depurado_num["TVIVHAB"]
df_porcentaje_categoria["VPH_NODREN_Perc_Nuevo"] = df_depurado_num["VPH_NODREN"] * 100 / df_depurado_num["TVIVHAB"]
df_porcentaje_categoria["VPH_PISOTI_Perc_Nuevo"] = df_depurado_num["VPH_PISOTI"] * 100 / df_depurado_num["TVIVHAB"]

print(df_porcentaje_categoria.head(10))

# Reorganizar las columnas
columnas_finales = [
    "CVEGEO", # clave geografica
    "PROM_OCUP","P3YM_HLI_Perc_Nuevo", "PHOGJEF_F_Perc_Nuevo", # categoría población
    "P15YM_AN_Perc_Nuevo","GRAPROES", # categoría educación
    "PSINDER_Perc_Nuevo", # categoría salud
    "PEA_Perc_Nuevo", "POB15_64_Perc_Nuevo", # categoría empleo
    "VPH_AGUAFV_Perc_Nuevo", "VPH_NODREN_Perc_Nuevo", "VPH_PISOTI_Perc_Nuevo" # categoría vivienda
]

# Asegurarse de que las columnas se encuentran en el orden deseado
df_porcentaje_indicadores = df_porcentaje_categoria[columnas_finales]
# Mostrar los primeros valores del DataFrame filtrado
print(df_porcentaje_indicadores.head(10))

# Calcular estadísticas 
# --------------------------------------------------------

# Definir las columnas de interés para calcular los valores
columnas_a_calcular = [col for col in columnas_finales if col != "CVEGEO"] # Excluir CVEGEO del calculo

# Calcular estadísticas para las columnas de interés
valores_min = df_porcentaje_indicadores[columnas_a_calcular].min()
valores_max = df_porcentaje_indicadores[columnas_a_calcular].max()
rangos = valores_max - valores_min
intervalos = rangos / 5

# Crear un DataFrame con los resultados
df_estadisticas_indicadores = pd.DataFrame({
    "Mínimo": valores_min,
    "Máximo": valores_max,
    "Rango": rangos,
    "Intervalo": intervalos
})

# Mostrar el resultado
print(df_estadisticas_indicadores)

# Generación de umbrales 
# ------------------------------------------------------

# Diccionario para almacenar los valores generados
valores_por_columna = {}

for columna in columnas_a_calcular:
    valores = [valores_max[columna]]  # Primer valor es el máximo
    
    # Generar los siguientes valores restando el intervalo
    for i in range(4):
        valores.append(valores[-1] - intervalos[columna])
    
    # Si la columna es "GRAPROES" o "PEA", invertir el orden
    if columna in ["GRAPROES", "PEA_Perc_Nuevo"]:
        valores.reverse()

    # Guardar los valores generados en el diccionario
    valores_por_columna[columna] = valores

# Convertir a DataFrame para visualizar mejor
df_umbrales_indicadores = pd.DataFrame(valores_por_columna, index=["V1", "V2", "V3", "V4", "V5"])

# Mostrar el resultado
print(df_umbrales_indicadores)

# Calificaciones 
# --------------------------------------------------------

"""
Ponderaciones por variable y umbral:

- Variables: ["PROM_OCUP", "P3YM_HLI_Perc_Nuevo", "PHOGJEF_F_Perc_Nuevo", "P15YM_AN_Perc_Nuevo", "POB15_64_Perc_Nuevo", "VPH_PISOTI_Perc_Nuevo"]
  - V5: 0.2
  - V4: 0.4
  - V3: 0.6
  - V2: 0.8
  - V1: 1.0

- Variables: ["PSINDER_Perc_Nuevo", "VPH_AGUAFV_Perc_Nuevo", "VPH_NODREN_Perc_Nuevo"]
  - V5: 0.4
  - V4: 0.8
  - V3: 1.2
  - V2: 1.6
  - V1: 2.0

- Variables: ["GRAPROES", "PEA_Perc_Nuevo"]
  - V1: 2.0
  - V2: 1.6
  - V3: 1.2
  - V4: 0.8
  - V5: 0.4
"""

# Función para asignar calificación basada en los valores y umbrales
def asignar_calificacion(columna, valor):
    
    if pd.isna(valor):
        return float('nan') # Si el valor es NaN, asignar NaN
    
    # Calificaciones para todas las columnas, incluyendo V1 en todas las comparaciones
    if columna in ["PROM_OCUP", "P3YM_HLI_Perc_Nuevo", "PHOGJEF_F_Perc_Nuevo", "P15YM_AN_Perc_Nuevo", "POB15_64_Perc_Nuevo", "VPH_PISOTI_Perc_Nuevo"]:
        if valor <= df_umbrales_indicadores[columna]["V5"]:
            return 0.2
        elif valor <= df_umbrales_indicadores[columna]["V4"]:
            return 0.4
        elif valor <= df_umbrales_indicadores[columna]["V3"]:
            return 0.6
        elif valor <= df_umbrales_indicadores[columna]["V2"]:
            return 0.8
        elif valor <= df_umbrales_indicadores[columna]["V1"]:
            return 1.0
    elif columna in ["PSINDER_Perc_Nuevo", "VPH_AGUAFV_Perc_Nuevo", "VPH_NODREN_Perc_Nuevo"]:
        if valor <= df_umbrales_indicadores[columna]["V5"]:
            return 0.4
        elif valor <= df_umbrales_indicadores[columna]["V4"]:
            return 0.8
        elif valor <= df_umbrales_indicadores[columna]["V3"]:
            return 1.2
        elif valor <= df_umbrales_indicadores[columna]["V2"]:
            return 1.6
        elif valor <= df_umbrales_indicadores[columna]["V1"]:
            return 2.0
    elif columna in ["GRAPROES", "PEA_Perc_Nuevo"]:
        if valor <= df_umbrales_indicadores[columna]["V1"]:
            return 2.0
        elif valor <= df_umbrales_indicadores[columna]["V2"]:
            return 1.6
        elif valor <= df_umbrales_indicadores[columna]["V3"]:
            return 1.2
        elif valor <= df_umbrales_indicadores[columna]["V4"]:
            return 0.8
        else:
            return 0.4

# Crear DataFrame
calificaciones_indicadores = pd.DataFrame()

# Aplicar la función a cada columna de interés y generar las nuevas columnas con las calificaciones
for columna in columnas_a_calcular:
    calificaciones_indicadores[f'Calificacion_{columna}'] = df_porcentaje_indicadores[columna].apply(lambda x: asignar_calificacion(columna, x))

# Seleccionar solo las columnas con las calificaciones
columnas_calificadas = [f'Calificacion_{columna}' for columna in columnas_a_calcular]
df_calificaciones_indicadores = calificaciones_indicadores[columnas_calificadas]

# Agregar la columna "CVEGEO" a los resultados
df_calificaciones_indicadores["CVEGEO"] = df_depurado["CVEGEO"]

# Mostrar el resultado
print(df_calificaciones_indicadores.head(5))

# Promedio por categoría 
# ------------------------------------------------------

# Crear DataFrame
df_promedio_categoria = pd.DataFrame()

# Crear nuevas columnas con el promedio de cada grupo
df_promedio_categoria["Promedio_Poblacion"] = df_calificaciones_indicadores[[
    "Calificacion_PROM_OCUP",  
    "Calificacion_P3YM_HLI_Perc_Nuevo",
    "Calificacion_PHOGJEF_F_Perc_Nuevo"
]].mean(axis=1)

df_promedio_categoria["Promedio_Educacion"] = df_calificaciones_indicadores[[
    "Calificacion_P15YM_AN_Perc_Nuevo", 
    "Calificacion_GRAPROES",  
    "Calificacion_PSINDER_Perc_Nuevo"
]].mean(axis=1)

df_promedio_categoria["Promedio_Salud"] = df_calificaciones_indicadores["Calificacion_PSINDER_Perc_Nuevo"]  # Solo una variable, se mantiene igual

df_promedio_categoria["Promedio_Empleo"] = df_calificaciones_indicadores[[
    "Calificacion_PEA_Perc_Nuevo",  
    "Calificacion_POB15_64_Perc_Nuevo"
]].mean(axis=1)

df_promedio_categoria["Promedio_Vivienda"] = df_calificaciones_indicadores[[
    "Calificacion_VPH_AGUAFV_Perc_Nuevo",  
    "Calificacion_VPH_NODREN_Perc_Nuevo",
    "Calificacion_VPH_PISOTI_Perc_Nuevo"
]].mean(axis=1)

# Agregar la columna "CVEGEO" a los resultados
df_promedio_categoria["CVEGEO"] = df_depurado["CVEGEO"]

# Mostrar las primeras filas para verificar
print(df_promedio_categoria.tail(5))

# Promedio General (5 categorías) 
# -------------------------------------------------------

# Crear DataFrame
df_promedio_general = pd.DataFrame()

# Calcular el promedio general basado en los promedios de cada categoría
df_promedio_general["Promedio_General"] = df_promedio_categoria[[
    "Promedio_Poblacion", "Promedio_Educacion", "Promedio_Salud", 
    "Promedio_Empleo", "Promedio_Vivienda"
]].mean(axis=1)

# Agregar la columna "CVEGEO" a los resultados
df_promedio_general["CVEGEO"] = df_depurado["CVEGEO"]

# Mostrar los primeros valores para verificar
print(df_promedio_general.head(5))

# Calcular estadísticas 
# -------------------------------------------------------

# Calcular estadísticas para la columna "Promedio_General"
minimo = df_promedio_general["Promedio_General"].min()
maximo = df_promedio_general["Promedio_General"].max()
rango = maximo - minimo
intervalo = rango / 5

# Crear un DataFrame con los resultados
df_estadisticas_promedio_general = pd.DataFrame({
    "Mínimo": [minimo],
    "Máximo": [maximo],
    "Rango": [rango],
    "Intervalo": [intervalo]
})

# Mostrar el DataFrame
print(df_estadisticas_promedio_general)

# Generación de umbrales 
# -------------------------------------------------------

# Crear una lista con los umbrales
umbrales_promedio_general = [maximo - i * intervalo for i in range(5)]

# Crear un DataFrame con los umbrales para visualizar (opcional)
df_umbrales_promedio_general = pd.DataFrame({"Promedio_General": umbrales_promedio_general}, index=["V1", "V2", "V3", "V4", "V5"])
print(df_umbrales_promedio_general)

# Aplicar el IVS 
# ------------------------------------------------------

# Definir función para asignar la categoría IVS correctamente
def asignar_ivs(valor, umbrales_promedio_general):
    if pd.isna(valor):  # Si el valor es NaN, devolver "Datos insuficientes"
        return "Datos insuficientes"
    elif valor <= umbrales_promedio_general["V5"]:
        return "Muy baja"
    elif valor <= umbrales_promedio_general["V4"]:
        return "Baja"
    elif valor <= umbrales_promedio_general["V3"]:
        return "Media"
    elif valor <= umbrales_promedio_general["V2"]:
        return "Alta"
    else:  # Si el valor es mayor a V2
        return "Muy alta"

# Crear el DataFrame df_ivs con la columna "Promedio_General" a partir de df_promedio_general
df_ivs = df_promedio_general.copy()

# Aplicar la función a la columna "Promedio_General" para asignar el valor de IVS
df_ivs["IVS"] = df_ivs["Promedio_General"].apply(lambda x: asignar_ivs(x, df_umbrales_promedio_general["Promedio_General"]))

# Agregar la columna "CVEGEO" a los resultados
df_ivs["CVEGEO"] = df_depurado["CVEGEO"].values 

# Mostrar los primeros valores para verificar
print(df_ivs.head(20))

# Contar las filas donde la columna 'IVS' tiene el valor "Datos insuficientes"
num_datos_insuficientes = (df_ivs['IVS'] == "Datos insuficientes").sum()
# Contar el total de filas en el DataFrame
total_filas = len(df_ivs)
# Calcular el porcentaje de filas con "Datos insuficientes"
porcentaje_datos_insuficientes = (num_datos_insuficientes / total_filas) * 100
# Mostrar los resultados
print(f"Número de filas con 'Datos insuficientes': {num_datos_insuficientes}")
print(f"Porcentaje de filas con 'Datos insuficientes': {porcentaje_datos_insuficientes:.2f}%")

# Clave geoestadística e IVS 
# ---------------------------------------------------------

# Seleccionar solo las columnas 'CVEGEO' e 'IVS'
df_cvegeo_ivs = df_ivs[['CVEGEO', 'IVS']]

# Visualizar las primeras filas en la terminal
print(df_cvegeo_ivs.head(10))

# Crear la ruta completa para el archivo a guardar
#file_path = os.path.join(folder_path, 'df_cvegeo_ivs.csv')
# Guardar el DataFrame como un archivo CSV
#df_cvegeo_ivs.to_csv(file_path, index=False)

# DataFrames Unidos
# ----------------------------------------------------------

import pandas as pd
from functools import reduce

# Lista de DataFrames
dfs = [df_porcentaje_indicadores, df_calificaciones_indicadores, df_promedio_categoria, df_promedio_general, df_cvegeo_ivs]
# Combinar todos los DataFrames en una sola línea
df_combined = reduce(lambda left, right: pd.merge(left, right, on='CVEGEO', how='outer'), dfs)
# Mostrar el DataFrame combinado
print(df_combined)

# Guardar DataFrames 
# ----------------------------------------------------------

# Lista de DataFrames que deseas guardar
dataframes = [
    df, 
    df_filtrado, 
    df_depurado, 
    df_porcentaje_indicadores, 
    df_estadisticas_indicadores, 
    df_umbrales_indicadores, 
    df_calificaciones_indicadores, 
    df_promedio_categoria, 
    df_promedio_general, 
    df_estadisticas_promedio_general, 
    df_umbrales_promedio_general, 
    df_ivs, 
    df_cvegeo_ivs,
    df_combined
]

# Nombres de los archivos CSV
csv_names = [
    "1_datos_originales.csv", 
    "2_datos_filtrados.csv", 
    "3_datos_depurados.csv", 
    "4_porcentaje_indicadores.csv", 
    "5_estadisticas_indicadores.csv", 
    "6_umbrales_indicadores.csv", 
    "7_calificaciones_indicadores.csv", 
    "8_promedio_categoria.csv", 
    "9_promedio_general.csv", 
    "10_estadisticas_promedio_general.csv", 
    "11_umbrales_promedio_general.csv", 
    "12_ivs.csv", 
    "13_cvegeo_ivs.csv",
    "14_df_combined.csv"
]

# Lista de DataFrames que deben incluir el índice en el CSV
dfs_con_indice = {"5_estadisticas_indicadores.csv", "6_umbrales_indicadores.csv"}

# Guardar cada DataFrame como un archivo CSV
for csv_name, df_to_save in zip(csv_names, dataframes):
    file_path = os.path.join(folder_path, csv_name)  # Crear ruta completa
    df_to_save.to_csv(file_path, index=(csv_name in dfs_con_indice))  # Incluir índice si está en la lista
    print(f"Archivo guardado: {csv_name} en la ruta: {file_path}")

# Diccionario de DataFrames 
# -------------------------------------------------------

descripciones = {
    "1_datos_originales.csv": "Datos originales sin modificaciones.",
    "2_datos_filtrados.csv": "Datos después de eliminar los resúmenes generales (totales) de las localidades.",
    "3_datos_depurados.csv": "Datos después de eliminar las columnas no deseadas para el análisis.",
    "4_porcentaje_indicadores.csv": "Cálculo de porcentaje por indicador respecto a la poblacion total o total de viviendas según corresponda.",
    "5_estadisticas_indicadores.csv": "Estadísticas descriptivas de los indicadores.",
    "6_umbrales_indicadores.csv": "Umbrales definidos para cada indicador.",
    "7_calificaciones_indicadores.csv": "Calificaciones asignadas a los indicadores.",
    "8_promedio_categoria.csv": "Promedio de indicadores por categoría.",
    "9_promedio_general.csv": "Promedio general de las categorías.",
    "10_estadisticas_promedio_general.csv": "Estadísticas del promedio general.",
    "11_umbrales_promedio_general.csv": "Umbrales establecidos para el promedio general.",
    "12_ivs.csv": "Índice de vulnerabilidad social calculado.",
    "13_cvegeo_ivs.csv": "Clave geográfica asociada al índice de vulnerabilidad social.",
    "14_df_combined.csv": "Base de datos completa."
}

# Crear la ruta del archivo de descripciones
file_path_descripciones = os.path.join(folder_path, "Diccionario_de_Datos.txt")

# Guardar descripciones en un archivo de texto
with open(file_path_descripciones, "w") as f:
    for csv_name, descripcion in descripciones.items():
        f.write(f"{csv_name}: {descripcion}\n")

print(f"Archivo de descripciones guardado en: {file_path_descripciones}")


