import pandas as pd
import numpy as np


# Downloadable at https://repositoriodeis.minsal.cl/DatosAbiertos/EGRESOS/Egresos_Hospitalarios_2020.zip

cols = [
    "ESTABLECIMIENTO_SALUD",
    "GLOSA_ESTABLECIMIENTO_SALUD",
    "SERVICIO_DE_SALUD",
    "SEXO",
    "TIPO_EDAD",
    "EDAD_CANT",
    "ANO_EGRESO",
    "FECHA_EGRESO",
    "AREA_FUNCIONAL_EGRESO",
    "DIAS_ESTADA",
    "CONDICION_EGRESO",
    "DIAG1",
    "GLOSA_DIAG1",
    "DIAG2",
    "GLOSA_DIAG2",
    "INTERV_Q",
    "PROCED",
    "CODIGO_PROCED_PPAL",
]

with open("data/egresos_2020.csv", "r", encoding="latin-1") as f:
    df = pd.read_csv(
        f,
        engine="c",
        sep=";",
        encoding="iso-8859-1",
        parse_dates=True,
        dayfirst=True,
        infer_datetime_format=True,
        error_bad_lines=False,
        true_values=["Pertenecientes al Sistema Nacional de Servicios de Salud, SNSS"],
        false_values=["No Pertenecientes al Sistema Nacional de Servicios de Salud, SNSS"],
        usecols=cols
    )

# Filtrar para solo 2020 y el Hospital San José de Melipilla
pacientes = df[((df["ANO_EGRESO"] == 2020) & (df["ESTABLECIMIENTO_SALUD"] == 110150))]
