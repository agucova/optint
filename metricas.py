def metricas(D, I, n_pacientes):
    with open('out.sol') as csv:
        aux = list(csv.readlines())
        aux = [linea.strip('\n').split(' ') for linea in aux]
        lista = []
        not_ideal = 0
        cambios_cama = 0
        distancia_total = 0
        for linea in aux:
            if linea[1] == '1':
                lista.append(linea)
                u = int(linea[0].split('[')[1].split(',')[1].strip(']'))
                p = int(linea[0].split('[')[1].split(',')[0])
                
                if 'alpha' in linea[0]:
                    not_ideal += 1
                
                if 'Z' in linea[0]:
                    cambios_cama += 1
                
                if 'Y' in linea[0]:
                    distancia_total += D[u - 1][I[p - 1] - 1]

        print(f"Hay {not_ideal/12} ({round(not_ideal / (n_pacientes * 12) * 100, 3)}%) pacientes en camas no ideales.")
        print("Número de cambios de cama:", cambios_cama)
        print("Distancia total:", distancia_total)