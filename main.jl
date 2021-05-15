using JuMP
using Gurobi

m = Model(Gurobi.Optimizer)

# Sets

P = range(271)
U = range(7)
F = range(9)
COV = range(4)
# B = TBD

# Parámetros
UMBRAL_CRITICO = 0.8
G = [paciente.g for paciente in pacientes]
I = [paciente.i for paciente in pacientes]
E_start = [paciente.e_start for paciente in pacientes]
E_end = [paciente.e_end for paciente in pacientes]
V = [paciente.v for paciente in pacientes]
S = [paciente.s for paciente in pacientes]
# A = {index: randint(0, 5) for index in T}

# Variables
@variables(m, begin
    y[p = P, u = U, f = F, t = T], Bin
    α[p = P, t= T], Bin
    Z[p = P], Bin
    dif[p = P, u = U, f = F, t = T], Bin
end)

@constraints(m, begin
    R1[u = U, f = F, t = T], (sum(Y[p, u, f, t] for p in p) <= C[u, f])

    R2₁[p = P, u = U, f = F, t = range(E_start[p] + 1, E_end[p] + 1)], (y[p, u, f, t - 1] - y[p, u, f, t] <= dif[p, u, f, t]),
    R2₂[p = P, u = U, f = F, t = range(E_start[p] + 1, E_end[p] + 1)], y[p, u, f, t] - y[p, u, f, t - 1] <= dif[p,u,f,t]
    R2₃[p = P, t = range(E_start[p] + 1, E_end[p] + 1)], sum(dif[p, u, f, t])
end)
