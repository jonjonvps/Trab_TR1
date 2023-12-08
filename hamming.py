def hamming(data):
    list_data = [int(d) for d in data]
    tamanho = len(list_data)
    print('Tamanho: ',tamanho)

    bitsParidade = 0
    # Calcula a quantidade de bits de paridades serao utilizados
    while (tamanho + bitsParidade) >= 2 ** bitsParidade:
        bitsParidade += 1

    print('Bits de paridade: ',bitsParidade)
    newData = [0] * (tamanho+bitsParidade)
    
    pow = 0
    # colocando os bits nos devidos lugares
    for i in range(tamanho+bitsParidade):
        # Como os bits de paridades são potencias de 2, adiciona o restante nos outros lugares
        if i+1 == 2 ** pow:
            pow += 1
        else:     
            newData[i] = list_data.pop(0)

    # Calculando os valores dos bits de paridades
    for i in range(bitsParidade):
        # verifica o bit mais significativo da posicao da lista com os bits de paridades
        # P1 = '1',  lista = '1', 1'1', 10'1', 11'1', 100'1', 101'1'
        # P2 = '1'0  lista = '1'1, 1'1'0, 1'1'', 101'1'0, 10'1'1
        # P3 = '1'00 lista = '1'00, '1'01, '1'10, '1'11
        # P4 = 1000  lista = '1'000, '1'001, '1'011
        for j in range(tamanho+bitsParidade):
            if (1<<i) & (j+1):
                newData[2**i - 1] = newData[2**i - 1] ^ newData[j]

    return newData

quadro = '1101001'
print(hamming(quadro))