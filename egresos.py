import pandas as pd
import numpy as np


# Downloadable at https://repositoriodeis.minsal.cl/DatosAbiertos/EGRESOS/Egresos_Hospitalarios_2020.zip

cols=["ESTABLECIMIENTO_SALUD", "GLOSA_ESTABLECIMIENTO_SALUD", "SERVICIO_DE_SALUD", "SEXO", "TIPO_EDAD", "EDAD_CANT", "ANO_EGR", "FECHA_EGR", "AREA_FUNCIONAL_EGRESO", "DIAS_ESTAD", "CONDICION_EGRESO", "DIAG1", "GLOSA_DIAG1", "DIAG2", "GLOSA_DIAG2", "INTERV_Q", "PROCED", "CODIGO_PROCED_PPAL"]

df = pd.read_csv("data/egresos.csv", engine="c", parse_dates=["FECHA_EGR"], dayfirst=True, memory_map=True, infer_datetime_format=True, true_values=["Pertenecientes al Sistema Nacional de Servicios de Salud, SNSS"],false_values=["No Pertenecientes al Sistema Nacional de Servicios de Salud, SNSS"], usecols=cols)

