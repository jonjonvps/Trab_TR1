import socket
import json

class Aplicacao:
    def socketRecive(self):
        HOST = 'localhost'
        PORT = 50000

        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        servidor.bind((HOST, PORT))

        servidor.listen()

        print("Aguardando conexão de um cliente")
        conn, ender = servidor.accept()

        print('Conectando em:', ender)

        while True:
            dados_recebidos = conn.recv(2048)
            if not dados_recebidos:
                print('Fechando a conexão')
                conn.close()
                break
            lista_recebida = json.loads(dados_recebidos.decode('utf-8'))
            print("Lista recebida:", lista_recebida)
            conn.sendall(str.encode('recebido'))



class CamadaFisica:
    def nrz_polar_dencoding(data):
        encoded_data = []

        for bit in data:
            if bit == -1:
                encoded_data.append(0)  # Mudança de polaridade para bit 0
            elif bit == 1:
                encoded_data.append(1)  # Nenhuma mudança de polaridade para bit 1
            else:
                raise ValueError("Os dados de entrada devem consistir apenas em 0s e 1s.")

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
    
class CamadaEnlace:

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

    def BitParidadeReverse(data):
        EDC = 0

        for bit in data:
            EDC ^= bit 

        data.pop()
        if(EDC):
            return data, 1
        else:
            return data, 0
        

    def crc_reverse(quadro):
        # Polinômio gerador CRC32-IEEE
        gx = 0x04C11DB7

        original_quadro = quadro[:-32]

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

    def hamming_receptor(data):

        tamanho = len(data)
        bitsParidade = 0
        # Calcula a quantidade de bits de paridades serao utilizados
        while (tamanho) >= 2 ** bitsParidade:
            bitsParidade += 1

        listbits = []
        for i in range(bitsParidade):
            # verifica o bit mais significativo da posicao da lista com os bits de paridades
            # P1 = '1',  lista = '1', 1'1', 10'1', 11'1', 100'1', 101'1'
            # P2 = '1'0  lista = '1'0, '1'1, 1'1'0, 1'1'', 101'1'0, 10'1'1
            # P3 = '1'00 lista = '1'00, '1'01, '1'10, '1'11
            # P4 = '1'000  lista = '1'000, '1'001, '1'011
            for j in range(2**i , tamanho):
                if (1<<i) & (j+1):
                    data[2**i - 1] = data[2**i - 1] ^ data[j]
        
            listbits.append(data[2**i - 1])

        print(listbits[::-1])

        erro = 0
        for i in range(bitsParidade-1,-1,-1):
            if(listbits[i] == 1):
                erro += 2**i

        if erro != 0:
            data[erro -1 ] = 1 - data[erro - 1]


        data_original = []
        pow = 0
        for i in range(tamanho):
            # Como os bits de paridades são potencias de 2, adiciona o restante nos outros lugares
            if i+1 == 2 ** pow:
                pow += 1
            else:     
                data_original.append(data[i])

        return data_original
    
teste = Aplicacao()
teste.socketRecive()