step.text("Creating R7 constraint...")
    m.addConstrs(
        (
            quicksum(Y[p, u, f, t] for f in F for u in COV) == V[p - 1]
            for p in P
            for t in range(E_start[p - 1], E_end[p - 1] + 1)
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
            for t in range(1, E_start[p - 1])
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
            for t in range(E_end[p - 1] + 1, T[-1] + 1)
        ),
        name="R9",
    )  # +1 para ser inclusivo
    step()

    # R10: Mientras esté en el hospital, p siempre tiene asignado 1 cama
    step.text("Creating R10 constraint...")
    m.addConstrs(
        (
            quicksum(Y[p, u, f, t] for u in U for f in F) == 1
            for p in P
            for t in range(E_start[p - 1], E_end[p - 1] + 1)
        ),
        name="R10",
    )
    step()