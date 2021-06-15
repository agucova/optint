def metricas(D, I, n_pacientes, B, G, Cama, Uni):
    with open('out_cama.sol', encoding='utf-8') as csv:
        aux = list(csv.readlines())[2:]
        aux = [linea.strip('\n').split(' ') for linea in aux]
        lista = []
        not_ideal = 0
        cambios_cama = 0
        distancia_total = 0
        pacientes_por_hora = [0]*12
        no_ideales_por_hora = [0]*12
        cambios_por_hora = [0]*12
        # digo cual es su cama si no lo he registrado
        Y = {}

        for linea in aux:
            if linea[1] == '1':
                # print(linea)
                lista.append(linea)
                index = list(map(int, linea[0].split('[')[1].strip(']').split(',')))
                if len(index) == 3:
                    p, i, t = index
                else:
                    p, t = index
                
                if 'alpha' in linea[0]:
                    not_ideal += 1
                
                if 'Z' in linea[0]:
                    cambios_cama += 1
                    cambios_por_hora[t] += 1
                
                if 'Y' in linea[0]:
                    distancia_total += D[Uni[i]][I[p]]
                    pacientes_por_hora[t] += 1
                    no_ideales_por_hora[t] += 1 if Cama[i] not in B[G[p]] else 0
                    # print(f"Y[{p}, {u}, {f}, {t}]")
                    if p not in Y:
                        Y[p] = (Cama[i], Cama[i])

                    Y[p] = (Y[p][0], Cama[i])
        
        no_ideales_inicio, no_ideales_final = 0, 0
        for p in Y:
            no_ideales_inicio += 1 if Y[p][0] not in B[G[p]] else 0
            no_ideales_final += 1 if Y[p][1] not in B[G[p]] else 0
                    
        # print(f"Pacientes en camas no ideales en un inicio: {no_ideales_inicio}")
        # print(f"Pacientes en camas ideales en el final: {no_ideales_final}")

        print("Número de cambios de cama:", cambios_cama)
        print("Distancia total:", distancia_total)
        print(
            "_" * 80,
            "Resultados por hora".center(80),
            "-" * 80,
            "",
            ' ' * 18 + "Pacientes   Camas no ideales    Cambios por hora",
            '\n'.join(
                f"Horas [{2*i: <2d}, {2*(i+1): >2d}]: {paciente: >8d}, {no_ideales_por_hora[i]: >14d}, {cambios_por_hora[i]: >15d}" 
                for i, paciente in enumerate(pacientes_por_hora)
            ),
            sep='\n'
        )
