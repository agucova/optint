from gurobipy import GRB, Model, quicksum, Env

def metrics(m, Y, alpha, Z, D, I, B, G, Cama, Uni, Q, S, N, P, T):
    not_ideal = 0
    beds_changed = 0
    total_distance = 0
    patients_per_hour = [0] * 12
    not_ideals_per_hour = [0] * 12
    changes_per_hour = [0] * 12

    for (p, i, t), value in Y.items():
        if int(round(value.X, 0)) == 1.0:
            total_distance += D[Uni[i]][I[p]]
            patients_per_hour[t] += 1
            not_ideals_per_hour[t] += 1 if Cama[i] not in B[G[p]] else 0

    for key, value in alpha.items():
        # print(value.X)
        if int(round(value.X, 0)) == 1:
            not_ideal += 1

    for (p, t), value in Z.items():
        if int(round(value.X, 0)) == 1:
            beds_changed += 1
            changes_per_hour[t] += 1

    # print("Número de cambios de cama:", beds_changed)
    # print("Distancia total:", total_distance)
    # print(
    #     "_" * 80,
    #     "Resultados por hora".center(80),
    #     "-" * 80,
    #     "",
    #     " " * 18 + "Pacientes   Camas no ideales    Cambios por hora",
    #     "\n".join(
    #         f"Horas [{2*i: <2d}, {2*(i+1): >2d}]: {paciente: >8d}, {not_ideals_per_hour[i]: >14d}, {changes_per_hour[i]: >15d}"
    #         for i, paciente in enumerate(patients_per_hour)
    #     ),
    #     sep="\n",
    # )
    return { 
        "total_distance": total_distance, 
        "beds_changed": beds_changed, 
        "not_ideal": not_ideal, 
        "status": m.status,
        "objetivo_1": quicksum(Y[p, i, t] * D[Uni[i]][I[p]] for i in N for p in P for t in T).getValue(),
        "objetivo_2": quicksum(Z[p, t] * (Q - S[p]) for p in P for t in T).getValue(),
        "objetivo_3": quicksum(alpha[p, t] for p in P for t in T).getValue()
    }
