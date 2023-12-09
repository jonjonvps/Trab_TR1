import numpy as np
import matplotlib.pyplot as plt  # (Opcional: para visualizar o sinal)

def ask(A, f, bit_stream):
    sig_size = len(bit_stream)
    signal = np.zeros(sig_size * 100)

    for i in range(sig_size):
        if bit_stream[i] == 1:
            for j in range(100):
                signal[i * 100 + j] = A * np.sin(2 * np.pi * f * j / 100)
        else:
            for j in range(100):
                signal[i * 100 + j] = 0

    return signal


def fsk(A, f1, f2, bit_stream):
    sig_size = len(bit_stream)
    signal = np.zeros(sig_size * 100)

    for i in range(sig_size):
        if bit_stream[i] == 1:
            for j in range(100):
                signal[i * 100 + j] = A * np.sin(2 * np.pi * f2 * j / 100)
        else:
            for j in range(100):
                signal[i * 100 + j] = A * np.sin(2 * np.pi * f1 * j / 100)

    return signal


def nrz_polar_encoding(data):
    encoded_data = []
    previous_level = 1  # Começamos com um nível positivo

    for bit in data:
        if bit == '0':
            encoded_data.append(-previous_level)  # Mudança de polaridade para bit 0
        elif bit == '1':
            encoded_data.append(previous_level)  # Nenhuma mudança de polaridade para bit 1
        else:
            raise ValueError("Os dados de entrada devem consistir apenas em 0s e 1s.")

    return encoded_data


def manchester_encoding(data):
    encoded_data = []
    list_data = [int(d) for d in data]
    clock =  []
    for _ in range(len(data)):
        clock.extend([0,1])

    for i in range(len(data)):
        encoded_data.extend([list_data[i] ^ clock[2*i], list_data[i] ^ clock[2*i+1]])

    return encoded_data

def manchester_dencoding(data):
    dencoded_data = []
    tamanho = len(data)/2
    for i in range(int(tamanho)):
        if data[2*i] == 1 and data[2*i+1] == 0:
            dencoded_data.append(1)
        else:
            dencoded_data.append(0)

    return dencoded_data

def bipolar_encoding(data):
    encoded_data = []
    voltage_level = 1  
    for bit in data:
        if bit == '0':
            # Para bit 0, a voltagem é zero
            encoded_data.append(0)
        elif bit == '1':
            # Para bit 1, alternamos entre voltagens positivas e negativas
            encoded_data.append(voltage_level)
            voltage_level = -voltage_level
        else:
            raise ValueError("Os dados de entrada devem consistir apenas em 0s e 1s.")

    return encoded_data

def bipolar_dencoding(data):
    dencoded_data = []
    voltage_level = 1  
    for bit in data:
        if bit == 0:
            # Para bit 0, a voltagem é zero
            dencoded_data.append(0)
        elif bit == 1 or bit == -1:
            # Para bit 1, alternamos entre voltagens positivas e negativas
            dencoded_data.append(voltage_level)
        else:
            raise ValueError("Os dados de entrada devem consistir apenas em 0s e 1s.")

    return dencoded_data

# Exemplo de uso
data_bits = "01010011"
nrz_polar_encoded = nrz_polar_encoding(data_bits)
print("Dados originais:", data_bits)
print("Codificação NRZ-Polar:", nrz_polar_encoded)


manchester_encoded = manchester_encoding(data_bits)
print("Dados originais:", data_bits)
print("Codificação Manchester:", manchester_encoded)

manchester_dencoded = manchester_dencoding(manchester_encoded)
print("Dados originais:", data_bits)
print("Decodificação Manchester:", manchester_dencoded)

bipolar_encoded = bipolar_encoding(data_bits)
print("Dados originais:", data_bits)
print("Codificação Bipolar:", bipolar_encoded)

bipolar_dencoded = bipolar_dencoding(bipolar_encoded)
print("Dados originais:", data_bits)
print("Decodificação Bipolar:", bipolar_dencoded)


#-----------------------------------------------------------------------------
test_str = "teste"

binary_str = ''.join(format(ord(i), '08b') for i in test_str)

print("strToBin: ",binary_str)

chunks = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]

# Converta cada parte binária em um caractere
decoded_str = ''.join(chr(int(chunk, 2)) for chunk in chunks)

print("String binária original:", binary_str)
print("String decodificada:", decoded_str)
#--------------------------------------------------------
A_amplitude = 1
f_frequencia = 1
f2_frequencia = 2
bit_stream_exemplo = [1, 0, 1, 1, 0]  # Substitua isso com sua sequência de bits

# Chama a função ask,e fsk
ask_signal = ask(A_amplitude, f_frequencia, bit_stream_exemplo)
fsk_signal = fsk(A_amplitude, f_frequencia,f2_frequencia, bit_stream_exemplo)

# (Opcional: Visualizar o sinal)
plt.subplot(2, 1, 1)
plt.plot(ask_signal, label='Sinal ASK')
plt.title('Sinal ASK')

plt.subplot(2, 1, 2)
plt.plot(fsk_signal, label='Sinal FSK')
plt.title('Sinal FSK')

plt.xlabel('Amostras')
plt.ylabel('Amplitude')
plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição
plt.show()

