from gurobipy import Model, GRB, quicksum
from paciente import Paciente
from random import randint
from alive_progress import alive_bar
# from debug import listen

with alive_bar(23, title="Optin't Model", force_tty=True, enrich_print=False) as step:
    step.text("Initializing gurobi model...")
    m = Model(name="Distribución de Camas")
    step()
    print()
    step.text("Generating sets...")
    # Sets
    P = range(1, 131)
    U = range(1, 9)
    F = range(1, 4)
    COV = range(1, 4)
    B = [
        {1},
        {1, 2},
        {1, 2, 3},
        {1, 2, 3, 4},
    ]  # rellenar sea el caso
    T = range(1, 13)
    step()

    step.text("Generating parameters...")
    # Parámetros
    C = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 38],
        [0, 0, 0, 30, 0],
        [0, 3, 3, 0, 0],
        [0, 0, 0, 12, 0],
        [0, 1, 1, 0, 8],
        [0, 0, 0, 0, 7],
        [0, 9, 9, 0, 0],
        [0, 7, 2, 0, 0],
    ]  # matriz

    D = [
        [],
        [0, 0, 5, 40, 35, 30, 25, 25, 15],
        [0, 5, 0, 35, 30, 25, 10, 20, 10],
        [0, 40, 35, 0, 5, 20, 30, 15, 25],
        [0, 35, 30, 5, 0, 15, 25, 10, 20],
        [0, 30, 25, 20, 15, 0, 15, 25, 35],
        [0, 25, 10, 30, 25, 15, 0, 15, 20],
        [0, 25, 20, 15, 10, 25, 15, 0, 10],
        [0, 15, 10, 25, 20, 35, 20, 10, 0],
    ]  # matriz

    UMBRAL_CRITICO = 0.8

    pacientes = [Paciente() for _ in P]

    G = [paciente.g for paciente in pacientes]
    I = [paciente.i for paciente in pacientes]
    E_start = [paciente.e_start for paciente in pacientes]
    E_end = [paciente.e_end for paciente in pacientes]
    V = [paciente.v for paciente in pacientes]
    S = [paciente.s for paciente in pacientes]
    A = {index: randint(0, 5) for index in T}  # hay que editarlo
    Cost = [10, 7, 2]  # TODO: Definir costos
    step()

    # Variables
    step.text("Creating variables...")
    Y = m.addVars(P, U, F, T, vtype=GRB.BINARY, name="Y")
    alpha = m.addVars(P, T, vtype=GRB.BINARY, name="alpha")
    Z = m.addVars(P, T, vtype=GRB.BINARY, name="Z")
    Dif = m.addVars(P, U, F, T, vtype=GRB.BINARY, name="Dif")
    step()

    # Constraints
    step.text("Creating constraints...")
    # R1: Se debe respetar la cantidad de camas f en todo u
    step.text("Creating R1 constraint...")
    m.addConstrs(
        (
            quicksum(Y[p, u, f, t] for p in P) <= C[u][f]
            for u in U
            for f in F
            for t in T
        ),
        name="R1",
    )
    step()

    # R2: Cambio de cama
    step.text("Creating R2.1 constraint...")
    m.addConstrs(
        (
            Y[p, u, f, t - 1] - Y[p, u, f, t] <= Dif[p, u, f, t]
            for p in P
            for u in U
            for f in F
            for t in range(E_start[p] + 1, E_end[p] + 1)
        ),
        name="R2.1",
    )
    step()
    step.text("Creating R2.2 constraint...")
    m.addConstrs(
        (
            Y[p, u, f, t] - Y[p, u, f, t - 1] <= Dif[p, u, f, t]
            for p in P
            for u in U
            for f in F
            for t in range(E_start[p] + 1, E_end[p] + 1)
        ),
        name="R2.2",
    )
    step()

    step.text("Creating R2.3 constraint...")
    m.addConstrs(
        (
            quicksum(Dif[p, u, f, t] for u in U for f in F) == 2 * Z[p, t]
            for p in P
            for t in range(E_start[p] + 1, E_end[p] + 1)
        ),
        name="R2.3",
    )
    step()

    step.text("Creating R2.4 constraint...")
    m.addConstrs(
        (Z[p, t] == 0 for p in P for t in range(1, E_start[p] + 1)), name="R2.4"
    )
    step()

    step.text("Creating R2.5 constraint...")
    m.addConstrs(
        (Z[p, t] == 0 for p in P for t in range(E_end[p] + 1, T[-1] + 1)), name="R2.5"
    )
    step()

    # R3: Hay un máximo de cambios por hora
    step.text("Creating R3 constraint...")
    m.addConstrs((quicksum(Z[p] for p in P) <= A[t] for t in T), name="R3")
    step()

    # R4: No se puede trasladar a los pacientes críticos
    step.text("Creating R4 constraint...")
    m.addConstrs((S[p, t] * Z[p, t] < UMBRAL_CRITICO for p in P for t in T), name="R4")
    step()

    # R5: Un paciente puede estar en una cama no ideal
    step.text("Creating R5 constraint...")
    m.addConstrs(
        (
            alpha[p] == 1 - quicksum(Y[p, u, f, t] for f in B[G[p]] for u in U)
            for p in P
            for t in range(E_start[p], E_end[p] + 1)
        ),
        name="R5",
    )
    step()

    # R6: Un paciente p no puede estar en 2 unidades y/o 2 tipos de cama al mismo tiempo.
    step.text("Creating R6 constraint...")
    m.addConstrs(
        (
            quicksum(Y[p, u, f, t] for u in U for f in F) == 1
            for p in P
            for t in range(E_start[p], E_end[p] + 1)
        ),
        name="R6",
    )
    step()

    # R7: Si p es COVID-19 positivo, solo puede ser asignado a una unidad COVID-19.
    step.text("Creating R7 constraint...")
    m.addConstrs(
        (
            (quicksum(Y[p, u, f, t] for f in F) for u in COV) == V[p]
            for p in P
            for t in T
        ),
        name="R7",
    )
    step()

    # R8: Antes de entrar p nno tienne asignada una cama
    step.text("Creating R8 constraint...")
    m.addConstrs(
        (
            quicksum(Y[p, u, f, t] for u in U for f in F) == 0
            for p in P
            for t in range(1, E_start[p])
        ),
        name="R8",
    )  # no le coloca el -1 porque no es inclusivo
    step()

    # R9: Después d salir, p no tendrá asignada una cama
    step.text("Creating R9 constraint...")
    m.addConstrs(
        (
            quicksum(Y[p, u, f, t] for u in U for f in F) == 0
            for p in P
            for t in range(E_end[p] + 1, T[-1] + 1)
        ),
        name="R9",
    )  # +1 para ser inclusivo
    step()

    # R10: Mientras esté en el hospital, p siempre tiene asignado 1 cama
    step.text("Creating R10 constraint...")
    m.addConstrs(
        (
            quicksum(Y[p, u, f, t] for u in U for f in F) == 0
            for p in P
            for t in range(E_start[p], E_end[p] + 1)
        ),
        name="R10",
    )
    step()

    # R11: p no puede ser trasladado más de X veces durante el día
    step.text("Creating R11 constraint...")
    m.addConstrs(
        (quicksum(Z[p, t] for t in range(E_start[p], E_end[p] + 1)) <= 2 for p in P),
        name="R11",
    )
    step()

    # Objective
    step.text("Creating objective function...")
    m.setObjective(
        quicksum(Y[p, u, f, t] * D[u][I[p]] for u in U for p in P for f in F for t in T)
        * Cost[0]
        + quicksum(Z[p, t] * (0.8 - S[p]) for p in P for t in T) * Cost[1]
        + quicksum(alpha[p] for p in P) * Cost[2],
        GRB.MINIMIZE,
    )
    step()

    step.text("Building model...")
    m.update()
    step()

    print("Finished model creation.")

    # Optimize
    print("Starting optimization.")
    m.optimize()
    step()

    # Write results
    print("Writing results")
    m.write("out.sol")
    step()

    print("Optimization finished succesfully.")

    # noqa: E741
