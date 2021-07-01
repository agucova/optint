from collections import defaultdict
from typing import List

from gurobipy import GRB, Env, Model, quicksum
from optint.model.metrics import metrics
from optint.model.parameters import gen_patients


def optimize_beds(n_beds: int, n_patients: int, cost: List[int], A=None, deterministic=True, cambios=1, Q=7, metrics_func=metrics, validation=False) -> dict:
    """Defines and optimizes the full bed distribution model.
    Returns whether it's feasible, the number of non-ideal beds, the number of changed beds and the total distance."""

    # Sets
    COV = range(3)
    B = [
        {0},
        {0, 1},
        {0, 1, 2},
        {0, 1, 2, 3},
    ]
    T = range(12)

    # Parámetros
    C = [
        [0, 0, 0, 38],
        [0, 0, 30, 0],
        [3, 3, 0, 0],
        [0, 0, 12, 0],
        [1, 1, 0, 8],
        [0, 0, 0, 7],
        [9, 9, 0, 0],
        [7, 2, 0, 0],
    ]  # matriz

    N = range(130)

    D = [
        [0, 5, 40, 35, 30, 25, 25, 15],
        [5, 0, 35, 30, 25, 10, 20, 10],
        [40, 35, 0, 5, 20, 30, 15, 25],
        [35, 30, 5, 0, 15, 25, 10, 20],
        [30, 25, 20, 15, 0, 15, 25, 35],
        [25, 10, 30, 25, 15, 0, 15, 20],
        [25, 20, 15, 10, 25, 15, 0, 10],
        [15, 10, 25, 20, 35, 20, 10, 0],
    ]  # matriz

    P, G, I, E_start, E_end, V, S = gen_patients(n_patients, deterministic=deterministic)
    if A is None:
        A = [0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 1, 1]
    # Q = 7

    # Tipo de cama
    Cama = [index for i in C for index, j in enumerate(i) for _ in range(j)]

    # Unidad
    Uni = [index for index, i in enumerate(C) for j in i for _ in range(j)]

    Aux = {(p, i): int(bool(Cama[i] in B[G[p]])) for i in N for p in range(n_patients)}

    COV = [i for i in N if Uni[i] in COV]


    with Env() as env, Model(env=env) as m:
        # Variables
        Y = m.addVars(P, N, T, vtype=GRB.BINARY, name="Y")
        alpha = m.addVars(P, T, vtype=GRB.BINARY, name="alpha")
        Z = m.addVars(P, T, vtype=GRB.BINARY, name="Z")

        # Constraints

        # R1: Se debe respetar la cantidad de camas f en todo u
        m.addConstrs(
            (quicksum(Y[p, i, t] for p in P) <= n_beds for i in N for t in T),
            name="R1",
        )

        # R2: Cambio de cama
        m.addConstrs(
            (
                Y[p, i, t - 1] - Y[p, i, t] <= Z[p, t]
                for p in P
                for i in N
                for t in range(E_start[p] + 1, E_end[p] + 1)
            ),
            name="R2.1",
        )
        m.addConstrs(
            (
                Y[p, i, t] - Y[p, i, t - 1] <= Z[p, t]
                for p in P
                for i in N
                for t in range(E_start[p] + 1, E_end[p] + 1)
            ),
            name="R2.2",
        )

        m.addConstrs(
            (Z[p, t] == 0 for p in P for t in range(E_start[p] + 1)), name="R2.3"
        )

        m.addConstrs(
            (Z[p, t] == 0 for p in P for t in range(E_end[p] + 1, T[-1] + 1)),
            name="R2.4",
        )

        # R3: Hay un máximo de cambios por cada 2 horas
        m.addConstrs((quicksum(Z[p, t] for p in P) <= A[t] for t in T), name="R3")

        # R4: No se puede trasladar a los pacientes críticos
        m.addConstrs((S[p] * Z[p, t] <= Q for p in P for t in T), name="R4")

        # R5: Un paciente puede estar en una cama no ideal
        m.addConstrs(
            (
                alpha[p, t] == 1 - quicksum(Y[p, i, t] * Aux[p, i] for i in N)
                for p in P
                for t in range(E_start[p], E_end[p] + 1)
            ),
            name="R5",
        )

        # R6: Mientras esté en el hospital, p siempre tiene asignado 1 cama
        m.addConstrs(
            (
                quicksum(Y[p, i, t] for i in N) == 1
                for p in P
                for t in range(E_start[p], E_end[p] + 1)
            ),
            name="R6",
        )

        # R7: Si p es COVID-19 positivo, solo puede ser asignado a una cama COVID-19.
        m.addConstrs(
            (
                quicksum(Y[p, i, t] for i in COV) == V[p]
                for p in P
                for t in range(E_start[p], E_end[p] + 1)
            ),
            name="R7",
        )

        # R8: Antes de entrar p no tiene asignada una cama
        m.addConstrs(
            (
                quicksum(Y[p, i, t] for i in N) == 0
                for p in P
                for t in range(E_start[p])
            ),
            name="R8",
        )

        # R9: Después de salir, p no tendrá asignada una cama
        m.addConstrs(
            (
                quicksum(Y[p, i, t] for i in N) == 0
                for p in P
                for t in range(E_end[p] + 1, T[-1] + 1)
            ),
            name="R9",
        )  # +1 para ser inclusivo

        # R10: p no puede ser trasladado más de 1 vez al el día
        m.addConstrs(
            (
                quicksum(Z[p, t] for t in range(E_start[p], E_end[p] + 1)) <= cambios
                for p in P
            ),
            name="R10",
        )

        # R11: un paciente máximo por cama
        m.addConstrs(
            (quicksum(Y[p, i, t] for p in P) <= 1 for i in N for t in T), name="R11"
        )

        # Objective
        m.setObjective(
            quicksum(Y[p, i, t] * D[Uni[i]][I[p]] for i in N for p in P for t in T)
            * cost[0]
            - quicksum(Z[p, t] * S[p] for p in P for t in T) * cost[1]
            + quicksum(alpha[p, t] for p in P for t in T) * cost[2]
            + quicksum(Z[p, t] for p in P for t in T) * cost[3],
            GRB.MINIMIZE,
        )

        m.update()

        # m.computeIIS() -> En caso de ser infactible se escribe en el archivo iis.ilp donde es infactible
        # m.write("archivo/iis.ilp") -> Acá lo escribe, se deben descomentar ambas lineas para visualizarlo

        m.optimize()
        # m.update()

        if m.status is GRB.OPTIMAL:
            m.write("out_cama.sol")
            return metrics_func(m, Y, alpha, Z, D, I, B, G, Cama, Uni, Q, S, N, P, T, A, E_start, E_end, COV, V, Aux, validation)
        general_metrics = defaultdict(lambda: m.status)
        return general_metrics, None
