# Optin't

 Modelo de optimización para mejorar la eficiencia y distribución de camas de un hospital. Creado para el curso Optimización (ICS1113) de la Escuela de Ingeniería UC.
## Instalación

El paquete requiere instalación por pip desde el directorio principal del repo:
```shell
pip install .
```

O en macOS y algunas versiones de Linux:
```shell
pip3 install .
```

Es importante señalar que esto implica que cambios hechos en los archivos no se reflejarán hasta instalar de nuevo el paquete. Por esto, si tienes Poetry instalado, es recomendado utilizar:
```shell
poetry install
```

## Correr
Para correr un ejemplo genérico del modelo de optimización y validar por tests todas las restricciones, puedes usar:

```shell
python optint/main.py
```

## Análisis
Bajo `analysis/` se pueden encontrar los notebooks de Jupyter utilizados para analizar distintas partes del modelo de optimización, como la resiliencia y el análisis de sensibilidad.
