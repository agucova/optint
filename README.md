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

Si tienes Poetry instalado, es recomendado utilizar:
```shell
poetry install
```

## Correr
Para correr un ejemplo genérico del modelo de optimización, puedes usar:

```shell
python optint/main.py
```

Y para validar las restricciones en bases a tests sobre la solución:

```shell
python optint/validation/validation.py
```