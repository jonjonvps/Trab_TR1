def insercao_byte(binary_data):
    bits_especial = '01111110'

    #binary_data = ''.join(format(ord(char), '08b') for char in data)
    frames = [binary_data[i:i+32] for i in range(0, len(binary_data), 32)]

    encapsulated_frames = []
    
    for frame in frames:
        cont = 0
        frame_checado = ''
        for bit in frame:
            if cont == 5:
                frame_checado += '0'
                cont = 0
            
            if bit == '1': 
                cont += 1 
            else: cont = 0

            frame_checado += bit

        encapsulated_frame = f"{bits_especial}{frame_checado}{bits_especial}"
        encapsulated_frames.append(encapsulated_frame)

    return encapsulated_frames

def reverse_byte(frames):
    binary_data = ''
    for frame in frames:
        # Verifica se o frame está no formato correto
        if not frame[:8].isdigit():
            raise ValueError("Formato de quadro inválido")

        #length_bin = frame[:8]
        frame_data = frame[8:]
        flag = 0
        cont = 0
        frame_descompactado = ''
        for bit in frame_data:
            if(flag):
                flag = 0; cont = 0
                frame_descompactado = frame_descompactado[:-7]
                continue

            if bit == '1':
                if cont == 5:
                    cont = 0; flag =1
                else:
                    cont += 1
            else:
                if cont == 5:
                    cont = 0
                    continue
                cont = 0
            frame_descompactado += bit
        
        binary_data += frame_descompactado 
    return binary_data

def frame_encapsulation(data):
    binary_data = ''.join(format(ord(char), '08b') for char in data)
    # list_bits = [int(d) for d in binary_data]
    print('Binara data: ',binary_data)
    frames = [binary_data[i:i+32] for i in range(0, len(binary_data), 32)]

    encapsulated_frames = []
    for frame in frames:
        length = len(frame)
        length_bin = format(length, '08b')
        encapsulated_frame = f"{length_bin}{frame}"
        encapsulated_frames.append(encapsulated_frame)

    return encapsulated_frames

def frame_decapsulation(frames):
    binary_data = ''
    for frame in frames:
        # Verifica se o frame está no formato correto
        if not frame[:8].isdigit():
            raise ValueError("Formato de quadro inválido")

        length_bin = frame[:8]
        frame_data = frame[8:]

        # Converte a representação binária do comprimento para um inteiro
        length = int(length_bin, 2)

        # Verifica se o comprimento do frame é consistente com o comprimento real dos dados
        if length != len(frame_data):
            raise ValueError("Comprimento do quadro inconsistente com os dados reais")

        binary_data += frame_data

    return binary_data

# Exemplo de uso
data_to_send = "Hello, World!"
encoded_frames = frame_encapsulation(data_to_send)
print("Quadros codificados:", encoded_frames)

try:
    decoded_data = frame_decapsulation(encoded_frames)
    print("Dados decodificados:", decoded_data)
    chunks = [decoded_data[i:i+8] for i in range(0, len(decoded_data), 8)]

    # Converta cada parte binária em um caractere
    decoded_str = ''.join(chr(int(chunk, 2)) for chunk in chunks)
    print("String decodificada:", decoded_str)
except ValueError as e:
    print(f"Erro ao decodificar: {e}")

data_to_send = "0000111100001111000011110000111100001111011111110000111100001111"
encoded_frames = insercao_byte(data_to_send)
print("Quadros codificados:", encoded_frames)

decoded_data = reverse_byte(encoded_frames)
print("Dados decodificados:", decoded_data)