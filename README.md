# optint

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
Para correr un ejemplo genérico del modelo de optimización, puedes usar:

```shell
python optint/main.py
```

Y para validar las restricciones en bases a tests sobre una solución generada en el momento:

```shell
python optint/validation/validation.py
```

## Análisis
Bajo `analysis/` se pueden encontrar los notebooks de Jupyter utilizados para analizar distintas partes del modelo de optimización, como la resiliencia y el análisis de sensibilidad.