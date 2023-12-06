def BitParidade(data):
    EDC = 0

    for bit in data:
        EDC ^= bit 

    data.append(EDC)
    return data


def BitParidadeReverse(data):
    EDC = 0

    for bit in data:
        EDC ^= bit 

    data.pop()
    if(EDC):
        return data, 1
    else:
        return data, 0

data = [0,1,1,1,1,0]

block = BitParidade(data)
print(block)
block[3] = 1 - block[3]
data_original, flag = BitParidadeReverse(data)
if(flag):
    print("Detectou erro: ", data_original)
else:
    print("Tudo certo: ", data_original) 