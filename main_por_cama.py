from gurobipy import Model, GRB, quicksum
from paciente import Paciente
from random import randint
from metricas_por_cama import metricas

m = Model(name="Distribución de Camas")

# 122 es el máximo factible que corre, no arreglamos los datos para obtener este resultado xD 
# El número máximo de pacientes en un día es de 122 a lo largo del 2020
# El número mínimo de pacientes en un día es de 27
# Promedio de pacientes por día es de 94
n_pacientes = 94

# Sets
P = range(n_pacientes)
U = range(8)
F = range(4)
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




camas_covid = sum(C[u][f] for u in COV for f in F)
pacientes = [Paciente(camas_covid) for _ in P]

G = [paciente.g for paciente in pacientes]
I = [paciente.i for paciente in pacientes]
E_start = [paciente.e_start for paciente in pacientes]
E_end = [paciente.e_end for paciente in pacientes]
V = [paciente.v for paciente in pacientes]
S = [paciente.s for paciente in pacientes]  # Arbitrario para el centro
A = [0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 1, 1]
#    0, 2, 4, 6, 8,10,12,14,16,18,20,22
Q = 8
Cost = [10, 3, 5]  # TODO: Definir costos

# Tipo de cama
Cama = [index for i in C for index, j in enumerate(i) for _ in range(j)]

# Unidad
Uni = [index  for index, i in enumerate(C) for j in i for _ in range(j)]

Aux = { (p, i): int(bool(Cama[i] in B[G[p]])) for i in N for p in range(n_pacientes) }

COV = [i for i in N if Uni[i] in COV]

# Variables
Y = m.addVars(P, N, T, vtype=GRB.BINARY, name="Y")
alpha = m.addVars(P, T, vtype=GRB.BINARY, name="alpha")
Z = m.addVars(P, T, vtype=GRB.BINARY, name="Z")
Dif = m.addVars(P, N, T, vtype=GRB.BINARY, name="Dif")

# Constraints

# R1: Se debe respetar la cantidad de camas f en todo u
m.addConstrs(
    (quicksum(Y[p, i, t] for p in P) <= 130 for i in N for t in T),
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

m.addConstrs((Z[p, t] == 0 for p in P for t in range(E_start[p] + 1)), name="R2.3")

m.addConstrs(
    (Z[p, t] == 0 for p in P for t in range(E_end[p] + 1, T[-1] + 1)), name="R2.4"
)

# R3: Hay un máximo de cambios por hora
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

# R6: Si p es COVID-19 positivo, solo puede ser asignado a una unidad COVID-19.
m.addConstrs(
    (
        quicksum(Y[p, i, t] for i in COV) == V[p]
        for p in P
        for t in range(E_start[p], E_end[p] + 1)
    ),
    name="R6",
)

# R7: Antes de entrar p no tiene asignada una cama
m.addConstrs(
    (
        quicksum(Y[p, i, t] for i in N) == 0
        for p in P
        for t in range(E_start[p])
    ),
    name="R7",
)

# R8: Después de salir, p no tendrá asignada una cama
m.addConstrs(
    (
        quicksum(Y[p, i, t] for i in N) == 0
        for p in P
        for t in range(E_end[p] + 1, T[-1] + 1)
    ),
    name="R8",
)  # +1 para ser inclusivo

# R9: Mientras esté en el hospital, p siempre tiene asignado 1 cama
m.addConstrs(
    (
        quicksum(Y[p, i, t] for i in N) == 1
        for p in P
        for t in range(E_start[p], E_end[p] + 1)
    ),
    name="R9",
)

# R10: p no puede ser trasladado más de 2 veces durante el día
m.addConstrs(
    (quicksum(Z[p, t] for t in range(E_start[p], E_end[p] + 1)) <= 1 for p in P),
    name="R10",
)

# R11: un paciente máximo por cama
m.addConstrs(
    (
        quicksum(Y[p, i, t] for p in P) <= 1
        for i in N
        for t in T
    ),
    name="R11"
)



# Objective
m.setObjective(
    quicksum(Y[p, i, t] * D[Uni[i]][I[p]] for i in N for p in P for t in T)
    * Cost[0]
    + quicksum(Z[p, t] * (Q - S[p]) for p in P for t in T) * Cost[1]
    + quicksum(alpha[p, t] for p in P for t in T) * Cost[2],
    GRB.MINIMIZE,
)

m.update()

print("Finished model creation.")

# m.computeIIS() -> En caso de ser infactible se escribe en el archivo iis.ilp donde es infactible
# m.write("archivo/iis.ilp") -> Acá lo escribe, se deben descomentar ambas lineas para visualizarlo
# # Optimize
print("Starting optimization.")
m.optimize()

# Write results
print("Writing results")
m.write("out_cama.sol")

metricas(D, I, n_pacientes, B, G, Cama, Uni)

# print("Optimization finished succesfully.")

# # noqa: E741
