from typing import Dict, Tuple

import pandas as pd
from gurobipy import quicksum


def metrics(
    m,
    Y,
    alpha,
    Z,
    D,
    I,
    B,
    G,
    Cama,
    Uni,
    Q,
    S,
    N,
    P,
    T,
    A,
    E_start,
    E_end,
    COV,
    V,
    Aux,
    validation=False,
) -> Tuple[Dict, pd.DataFrame]:
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

    if validation and m.status == 2.0:
        print_validation(
            m,
            Y,
            alpha,
            Z,
            D,
            I,
            B,
            G,
            Cama,
            Uni,
            Q,
            S,
            N,
            P,
            T,
            A,
            E_start,
            E_end,
            COV,
            V,
            Aux,
        )

    # Funcion vieja, cambiar nombres del input
    # prints_per_blocks(beds_changed, total_distance, not_ideals_per_hour, changes_per_hour, patients_per_hour)

    general_metrics = {
        "total_distance": total_distance,
        "beds_changed": beds_changed,
        "not_ideal": not_ideal,
        "status": m.status,
        "objective_1": quicksum(
            Y[p, i, t] * D[Uni[i]][I[p]] for i in N for p in P for t in T
        ).getValue(),
        "objective_2": quicksum(Z[p, t] * S[p] for p in P for t in T).getValue(),
        "objective_3": quicksum(alpha[p, t] for p in P for t in T).getValue(),
        "objective_4": quicksum(Z[p, t] for p in P for t in T).getValue(),
    }

    metrics_by_block = {
        "time": [2 * t for t in T],
        "changes_per_block": changes_per_block,
        "not_ideals_per_block": not_ideals_per_block,
        "patients_per_block": patients_per_block,
        "dist_per_block": dist_per_block,
    }
    metrics_by_block = pd.DataFrame.from_dict(
        metrics_by_block, orient="index"
    ).transpose()
    return general_metrics, metrics_by_block


def prints_per_blocks(
    beds_changed,
    total_distance,
    not_ideals_per_hour,
    changes_per_hour,
    patients_per_hour,
):
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


def print_validation(
    m, Y, alpha, Z, D, I, B, G, Cama, Uni, Q, S, N, P, T, A, E_start, E_end, COV, V, Aux
):
    flag_paciente_por_camas = False
    for t in T:
        for i in N:
            if quicksum(Y[p, i, t] for p in P).getValue() > 1.0 + 1e-6:
                print("No se respeta mas de una cama")
                flag_paciente_por_camas = True

    if flag_paciente_por_camas:
        print("No se respeta la cantidad de pacientes por cama")
    else:
        print("✅ Se respetó la cantidad de pacientes por cama")

    # Restriccion 2
    flag_cambio_cama = False
    for p in P:
        for i in N:
            for t in range(E_start[p] + 1, E_end[p] + 1):
                if (Y[p, i, t - 1] - Y[p, i, t]).getValue() > Z[p, t].X:
                    print("No se cumple R21", p, i, t)
                    flag_cambio_cama = True
                if (Y[p, i, t] - Y[p, i, t - 1]).getValue() > Z[p, t].X:
                    print("No se cumple R22", p, i, t)
                    flag_cambio_cama = True

    for p in P:
        for t in range(E_start[p] + 1):
            if abs(Z[p, t].X) >= 1e-6:
                print("No se cumple R23", p, i, t)
                flag_cambio_cama = True
        for t in range(E_end[p] + 1, T[-1] + 1):
            if abs(Z[p, t].X) >= 1e-6:
                print("No se cumple R24", p, i, t)
                flag_cambio_cama = True
    if flag_cambio_cama:
        print("No se respetan los cambios de camas")
    else:
        print("✅ Se respetan los cambios de camas")

    # Restriccion 3
    flag_cantidad_maxima_cambios = False
    for t in T:
        if quicksum(Z[p, t] for p in P).getValue() > A[t]:
            print("te pasaste carnal")
            flag_cantidad_maxima_cambios = True

    if flag_cantidad_maxima_cambios:
        print("No se respetan los cambios máximos")
    else:
        print("✅ Se respetan los cambios máximos")

    # Restricción 4
    flag_solo_pacientes_severos = False
    for p in P:
        for t in T:
            if S[p] * Z[p, t].X > Q:
                print("moviste a alguien que esta gg")
                flag_solo_pacientes_severos = True

    if flag_solo_pacientes_severos:
        print("No se respetan los impedimientos de movilización")
    else:
        print("✅ Se respetan los impedimientos de movilización")

    # Restriccion 5
    flag_cama_ideal = False
    for p in P:
        for t in range(E_start[p], E_end[p] + 1):
            if (
                1.0 - quicksum(Y[p, i, t] * Aux[p, i] for i in N).getValue()
                != alpha[p, t].X
            ):
                flag_cama_ideal = True
    if flag_cama_ideal:
        print("No se respetan las camas ideales")
    else:
        print("✅ Se respetan las camas ideales")

    # Restriccion 6
    flag_pacientes_en_una_misma_cama = False
    for p in P:
        for t in range(E_start[p], E_end[p] + 1):
            if quicksum(Y[p, i, t] for i in N).getValue() != 1.0:
                flag_pacientes_en_una_misma_cama = True

    if flag_pacientes_en_una_misma_cama:
        print("No se respeta la cantidad de gente en una misma cama")
    else:
        print("✅ Se respeta la cantidad de gente en una misma cama")

    # Restriccion 7
    flag_paciente_covid_en_su_debida_cama = False
    for p in P:
        for t in range(E_start[p], E_end[p] + 1):
            if quicksum(Y[p, i, t] for i in COV).getValue() != V[p]:
                flag_paciente_covid_en_su_debida_cama = True

    if flag_paciente_covid_en_su_debida_cama:
        print("No se respeta que la gente tenga covid solo esté en su zona")
    else:
        print("✅ Se respeta que la gente tenga covid solo esté en su zona")

    # Restriccion 8
    flag_cama_no_asignada = False
    for p in P:
        for t in range(E_start[p]):
            if quicksum(Y[p, i, t] for i in N).getValue() != 0.0:
                flag_cama_no_asignada = True

    if flag_cama_no_asignada:
        print("No se respeta que la gente no tenga cama antes de entrar")
    else:
        print("✅ Se respeta que la gente no tenga cama antes de entrar")

    # Restriccion 9
    flag_cama_asignada = False
    for p in P:
        for t in range(E_end[p] + 1, T[-1] + 1):
            if quicksum(Y[p, i, t] for i in N).getValue() != 0:
                flag_cama_asignada = True

    if flag_cama_asignada:
        print("No se respeta que la gente no tenga cama después de salir")
    else:
        print("✅ Se respeta que la gente no tenga cama después de salir")

    # Restriccion 10
    flag_traslados_diarios = False
    for p in P:
        if quicksum(Z[p, t] for t in range(E_start[p], E_end[p] + 1)).getValue() > 1:
            flag_traslados_diarios = True

    if flag_traslados_diarios:
        print("No se respeta que la gente sea trasladada al menos una vez")
    else:
        print("✅ Se respeta que la gente sea trasladada al menos una vez")
