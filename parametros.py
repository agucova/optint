with open('Distancias.csv', encoding='utf-8') as csv:
    aux = list(csv.readlines())
    for i in range(len(aux)):
        aux[i] = aux[i].strip('\n').split(',')

    lista = []
    for index, linea in enumerate(aux):
        if index in range(1, 9):
            linea = linea[1:]
            linea = [int(x) for x in linea]
            lista.append(linea)
    # print(*lista, sep='\n')

with open('Cuf.csv', encoding='utf-8') as csv:
    lista = list(csv.readlines())
    lista = [linea.strip('\n').split(',') for linea in lista]
    lista = [[int(x) for x in linea] for linea in lista]
    print(*lista, sep='\n')