from gurobipy import Model, GRB, quicksum
from parametros import *
from paciente import Paciente
from random import randint

m = Model(name="Distribución de Camas")

# Sets

P = range(1, 271)
U = range(1, 7)
F = range(1, 9)
COV = range(1, 4)
B = [set() for u in U]  # rellenar sea el caso
T = range(1, 25)


# Parámetros
C = {}  # matriz
D = {}  # matriz

UMBRAL_CRITICO = 0.8

pacientes = [Paciente() for _ in P]

G = [paciente.g for paciente in pacientes]
I = [paciente.i for paciente in pacientes]
E_start = [paciente.e_start for paciente in pacientes]
E_end = [paciente.e_end for paciente in pacientes]
V = [paciente.v for paciente in pacientes]
S = [paciente.s for paciente in pacientes]
A = {index: randint(0, 5) for index in T}  # hay que editarlo


# Variables
Y = m.addVars(P, U, F, T, vtype=GRB.BINARY, name="Y")
alpha = m.addVars(P, T, vtype=GRB.BINARY, name="alpha")
Z = m.addVars(P, T, vtype=GRB.BINARY, name="Z")
Dif = m.addVars(P, U, F, T, vtype=GRB.BINARY, name="Dif")

# Constraints

# R1: Se debe respetar la cantidad de camas f en todo u
m.addConstr(
    (quicksum(Y[p, u, f, t] for p in P) <= C[u, f] for u in U for f in F for t in T),
    name="R1",
)


# R2: Cambio de cama
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

m.addConstrs(
    (
        quicksum(Dif[p, u, f, t] for u in U for f in F) == 2 * Z[p, t]
        for p in P
        for t in range(E_start[p] + 1, E_end[p] + 1)
    ),
    name="R2.3",
)

m.addConstrs((Z[p, t] == 0 for p in P for t in range(1, E_start[p] + 1)), name="R2.4")

m.addConstrs(
    (Z[p, t] == 0 for p in P for t in range(E_end[p] + 1, T[-1] + 1)), name="R2.5"
)


# R3: Hay un máximo de cambios por hora
m.addConstrs((quicksum(Z[p] for p in P) <= A[t] for t in T), name="R3")


# R4: No se puede trasladar a los pacientes críticos
m.addConstrs((S[p, t] * Z[p, t] < UMBRAL_CRITICO for p in P for t in T), name="R4")
# Pregunta, no es mejor tener una restriccion con <=? o >=?
# para este caso al ser binario funcionan las desiguadades del tipo < >, le había preguntado a
# jaimito en una clase y dijo que sí


# R5: Un paciente puede estar en una cama no ideal
# TODO: (Como modelamos B_G_p?)
# m.addConstrs((alpha[p] == 1 - quicksum(...)), name="R5")


# R6: Un paciente p no puede estar en 2 unidades y/o 2 tipos de cama al mismo tiempo.
m.addConstrs(
    (
        quicksum(Y[p, u, f, t] for u in U for f in F) == 1
        for t in range(E_start[p], E_end[p] + 1)
        for p in P
    ),
    name="R6",
)


# R7: Si p es COVID-19 positivo, solo puede ser asignado a una unidad COVID-19.
# TODO: COV definido?
m.addConstrs(
    ((quicksum(Y[p, u, f, t] for f in F) for u in COV) == V[p] for p in P for t in T),
    name="R7",
)


# R8: Antes de entrar p nno tienne asignada una cama
m.addConstrs(
    (
        quicksum(Y[p, u, f, t] for u in U for f in F) == 0
        for p in P
        for t in range(1, E_start[p])
    ),
    name="R8",
)  # no le coloca el -1 porque no es inclusivo

# R9: Después d salir, p no tendrá asignada una cama
m.addConstrs(
    (
        quicksum(Y[p, u, f, t] for u in U for f in F) == 0
        for p in P
        for t in range(E_end[p] + 1, T[-1] + 1)
    ),
    name="R9",
)  # +1 para ser inclusivo


# R10: Mientras esté en el hospital, p siempre tiene asignado 1 cama
m.addConstrs(
    (
        quicksum(Y[p, u, f, t] for u in U for f in F) == 0
        for p in P
        for t in range(E_start[p], E_end[p] + 1)
    ),
    name="R10",
)


# R11: p no puede ser trasladado más de X veces durante el día
# TODO: definir X
# TODO: p a la derecha no existe
m.addConstrs(
    (quicksum(Z[p, t] for p in P) <= x for t in range(E_start[p], E_end[p] + 1)),
    name="R11",
)


# Objective


# m.setObjective(w, GRB.MINIMIZE)

# Optimize
m.optimize()

# Write results
m.write("out.sol")


# noqa: E741
