from optint.model.model import optimize_beds

# Correr instancia de nuestro modelo con costos ideales.
# Código de gurobi en optint/model/model.py
general_metrics, metrics_by_block = optimize_beds(130, 100, [1, 5, 20, 35], validation=True)
print(f"{general_metrics = }")