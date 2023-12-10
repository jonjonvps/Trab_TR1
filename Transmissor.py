import numpy as np
import socket
import json

class Aplicacao:
    def strTobit(self, text):
        binary_str = ''.join(format(ord(i), '08b') for i in text)
        return binary_str
    
    def srtBitToList(self, data):
        list_data = [int(d) for d in data]
        return list_data
    
    def listToStr(self, data):
        strbits = ''.join(str(bit) for bit in data)
        return strbits
    

    def socketsend(self, data):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        endereco_servidor = ('localhost', 12345)  # Escolha um número de porta adequado
        servidor.bind(endereco_servidor)
        servidor.listen()

        print("Aguardando conexão...")
        conexao, endereco_cliente = servidor.accept()

        # Enviar dados para o Receptor
        dados_a_enviar = json.dumps(data)
        conexao.sendall(dados_a_enviar.encode('utf-8'))

        # Encerrar conexão
        conexao.close()

    
    def aplicar(self, text_input, encoding, framing, error_detection, modulation_str):
        bin_str = self.strTobit(text_input)

        if framing == 'Inserção de Byte':
            quadros = CamadaEnlace.insercao_byte(bin_str)
        else:
            quadros = CamadaEnlace.frame_encapsulation(bin_str)

        listBytesErro = []
        if error_detection == 'CRC':
            for quadro in quadros:
                lista = self.srtBitToList(quadro)
                bitsErro = CamadaEnlace.crc(lista)
                listBytesErro.append(bitsErro)
        elif error_detection == 'Bits de Paridade':
            for quadro in quadros:
                lista = self.srtBitToList(quadro)
                bitsErro = CamadaEnlace.BitParidade(lista)
                listBytesErro.append(bitsErro)
        else:
            for quadro in quadros:
                lista = self.srtBitToList(quadro)
                bitsErro = CamadaEnlace.hamming(lista)
                listBytesErro.append(bitsErro)

        listBytesEncoded = []
        if encoding == 'NRZ Polar':
            for quadro in listBytesErro:
                print(quadro)
                quadro_str = self.listToStr(quadro)
                quadro_encode = CamadaFisica.nrz_polar_encoding(quadro_str)
                listBytesEncoded.append(quadro_encode)

        elif encoding == 'Manchester':
            for quadro in listBytesErro:
                quadro_str = self.listToStr(quadro)
                quadro_encode = CamadaFisica.manchester_encoding(quadro_str)
                listBytesEncoded.append(quadro_encode)

        else:
            for quadro in listBytesErro:
                quadro_str = self.listToStr(quadro)
                quadro_encode = CamadaFisica.bipolar_encoding(quadro_str)
                listBytesEncoded.append(quadro_encode)


        A_amplitude = 1
        f_frequencia = 1
        f2_frequencia = 2
        listModulacao = []
        if 'Modulação ASK' in modulation_str:
            for quadro in listBytesEncoded:
                modulo = CamadaFisica.ask(A_amplitude,f_frequencia,quadro)
                listModulacao.append(modulo)
        else:
            for quadro in listBytesEncoded:
                modulo = CamadaFisica.fsk(A_amplitude,f_frequencia,f2_frequencia,quadro)
                listModulacao.append(modulo)

        
        
        return bin_str, quadros[0], listBytesErro[0], listBytesEncoded[0]
        
class CamadaFisica:
    def nrz_polar_encoding(data):
        encoded_data = []
        previous_level = 1  # Começamos com um nível positivo

        for bit in data:
            if bit == '0':
                encoded_data.append(-previous_level) # Mudança de polaridade para bit 0
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

    
class CamadaEnlace:
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
                    print("passou")
                
                if bit == '1': 
                    cont += 1 
                else: cont = 0

                frame_checado += bit

            encapsulated_frame = f"{bits_especial}{frame_checado}{bits_especial}"
            encapsulated_frames.append(encapsulated_frame)

        return encapsulated_frames

    def frame_encapsulation(data):
        # binary_data = ''.join(format(ord(char), '08b') for char in data)
        # list_bits = [int(d) for d in binary_data]
        frames = [data[i:i+32] for i in range(0, len(data), 32)]

        encapsulated_frames = []
        for frame in frames:
            length = len(frame)
            length_bin = format(length, '08b')
            encapsulated_frame = f"{length_bin}{frame}"
            encapsulated_frames.append(encapsulated_frame)

        return encapsulated_frames

    def BitParidade(data):
        EDC = 0

        for bit in data:
            EDC ^= bit 

        data.append(EDC)
        return data
    
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
        return copy
    
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

