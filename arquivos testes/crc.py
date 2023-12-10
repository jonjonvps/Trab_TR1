def crc(quadro):
    # Polinômio gerador CRC32-IEEE
    g = 0x04C11DB7

    copy = quadro.copy()

    # Adiciona 32 bits de zeros ao final da cópia
    copy.extend([0] * 32)

    tamanho = len(quadro)

    # Calcula o resto da divisao
    for i in range(tamanho):
        # Pula se for 0
        if not copy[i]:
            continue

        # XOR com o termo x^32, sempre vai ser 0
        copy[i] = 0

        # XOR com os demais termos
        for j in range(32):
            if g & (1 << j):
                copy[i + 32 - j] = 1 - copy[i + 32 - j]

    # O código CRC (remainder) é retornado
    return copy[tamanho:]


def crc_reverse(quadro):
    # Polinômio gerador CRC32-IEEE
    gx = 0x04C11DB7

    original_quadro = quadro[:-32]
    print("original: ", original_quadro)

    tamanho = len(original_quadro)

    # Calcula o resto da divisao
    for i in range(tamanho):
        if not quadro[i]:
            continue

        # XOR com o termo x^32
        quadro[i] = 0

        # XOR com os demais termos
        for j in range(32):
            if gx & (1 << j):
                quadro[i + 32 - j] = 1 - quadro[i + 32 - j]
    
    return original_quadro, quadro[tamanho:]

def listToStr(data):
    strbits = ''.join(str(bit) for bit in data)
    return strbits


# Exemplo de uso:
quadro = [1, 0, 1, 1, 0, 0, 1, 0, 0, 1]  # Substitua pelos seus dados
resultado_crc = crc(quadro)
print("Código CRC calculado:", resultado_crc)


quadro.extend(resultado_crc)

print("Quadro com CRC: ", quadro)

quadro_original, resultado_crc = crc_reverse(quadro)
print("Resultado do CRC: ",resultado_crc)
print("Quadro original: ", quadro_original)

if 1 in resultado_crc:
    print("apresentou erro")
else:
    print("Não teve erro")