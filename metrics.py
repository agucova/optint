from gurobipy import GRB, Model, quicksum, Env
from typing import Tuple, Dict
import pandas as pd

def metrics(m, Y, alpha, Z, D, I, B, G, Cama, Uni, Q, S, N, P, T) -> Tuple[Dict, pd.DataFrame]:
    not_ideal = 0
    beds_changed = 0
    total_distance = 0
    patients_per_block = [0] * 12
    not_ideals_per_block = [0] * 12
    changes_per_block = [0] * 12
    dist_per_block = [0] * 12

    for (p, i, t), value in Y.items():
        if int(round(value.X, 0)) == 1.0:
            total_distance += D[Uni[i]][I[p]]
            patients_per_block[t] += 1
            not_ideals_per_block[t] += 1 if Cama[i] not in B[G[p]] else 0
            dist_per_block[t] += D[Uni[i]][I[p]]

    for (p, t), value in alpha.items():
        # print(value.X)
        if int(round(value.X, 0)) == 1:
            not_ideal += 1

    for (p, t), value in Z.items():
        if int(round(value.X, 0)) == 1:
            beds_changed += 1
            changes_per_block[t] += 1

    # prints_per_blocks(beds_changed, total_distance, not_ideals_per_hour, changes_per_hour, patients_per_hour):

    general_metrics = { 
        "total_distance": total_distance, 
        "beds_changed": beds_changed, 
        "not_ideal": not_ideal, 
        "status": m.status,
        "objective_1": quicksum(Y[p, i, t] * D[Uni[i]][I[p]] for i in N for p in P for t in T).getValue(),
        "objective_2": quicksum(Z[p, t] * S[p] for p in P for t in T).getValue(),
        "objective_3": quicksum(alpha[p, t] for p in P for t in T).getValue()
    }
    
    metrics_by_block = {
        "time": [2*t for t in T],
        "changes_per_block": changes_per_block,
        "not_ideals_per_block": not_ideals_per_block,
        "patients_per_block": patients_per_block,
        "dist_per_block": dist_per_block,
    }
    metrics_by_block = pd.DataFrame.from_dict(metrics_by_block, orient='index').transpose()
    return general_metrics, metrics_by_block

def prints_per_blocks(beds_changed, total_distance, not_ideals_per_hour, changes_per_hour, patients_per_hour):
    print("Número de cambios de cama:", beds_changed)
    print("Distancia total:", total_distance)
    print(
        "_" * 80,
        "Resultados por hora".center(80),
        "-" * 80,
        "",
        " " * 18 + "Pacientes   Camas no ideales    Cambios por hora",
        "\n".join(
            f"Horas [{2*i: <2d}, {2*(i+1): >2d}]: {paciente: >8d}, {not_ideals_per_hour[i]: >14d}, {changes_per_hour[i]: >15d}"
            for i, paciente in enumerate(patients_per_hour)
        ),
        sep="\n",
    )