import socket
import json
import pickle

class Aplicacao:
    def bitToStr(self, binary_str):
        chunks = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]

        # Converta cada parte binária em um caractere
        encoded_str = ''.join(chr(int(chunk, 2)) for chunk in chunks)
        return encoded_str

    def strTobit(self, text):
        binary_str = ''.join(format(ord(i), '08b') for i in text)
        return binary_str
    
    def srtBitToList(self, data):
        list_data = [int(d) for d in data]
        return list_data
    
    def listToStr(self, data):
        strbits = ''.join(str(bit) for bit in data)
        return strbits
    
    def socketsend(self, text, erro, Dencoded, BytesErro, Framing, bits):
        HOST = 'localhost'
        PORT = 20000
        data= []
        print("lista decode",Dencoded)
        data.append(text), data.append(erro), data.append(Dencoded), data.append(BytesErro), data.append(Framing), data.append(bits)
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            cliente.connect((HOST,PORT))
            dados_a_enviar = json.dumps(data)
            cliente.sendall(dados_a_enviar.encode('utf-8'))

            menssage = cliente.recv(2048)

            print('Mensagem Socket: ', menssage.decode())
        finally:
            cliente.close()


    def aplicar(self,data):
        data_original = data[:-3]
        encoding, framing, error_detection = data[-3:]

        listBytesDencoded = []
        if encoding == 'NRZ Polar':
            for quadro in data_original:
                quadro_encode = CamadaFisica.nrz_polar_dencoding(quadro)
                listBytesDencoded.append(quadro_encode)

        elif encoding == 'Manchester':
            for quadro in data_original:
                quadro_encode = CamadaFisica.manchester_dencoding(quadro)
                listBytesDencoded.append(quadro_encode)

        else:
            for quadro in data_original:
                quadro_encode = CamadaFisica.bipolar_dencoding(quadro)
                listBytesDencoded.append(quadro_encode)

        decoder = []
        decoder.extend(listBytesDencoded[0])
        
        listBytesErro = []
        if error_detection == 'CRC':
            for quadro in listBytesDencoded:
                bitsErro, erro = CamadaEnlace.crc_reverse(quadro)
                listBytesErro.append(bitsErro)
        elif error_detection == 'Bits de Paridade':
            for quadro in listBytesDencoded:
                bitsErro, erro = CamadaEnlace.BitParidadeReverse(quadro)
                listBytesErro.append(bitsErro)
        else:
            for quadro in listBytesDencoded:
                bitsErro, erro = CamadaEnlace.hamming_receptor(quadro)
                listBytesErro.append(bitsErro)

        print("lista de erros: ",listBytesErro)
        listFramig = []
        for quadro in listBytesErro:
            str_bin = self.listToStr(quadro)
            listFramig.append(str_bin)

        if framing == 'Inserção de Byte':
            bits = CamadaEnlace.reverse_byte(listFramig)
        else:
            bits = CamadaEnlace.frame_decapsulation(listFramig)

        text = self.bitToStr(bits)
        if erro == 1:
            msg = 'Apresentou erro!'
        else:
            msg = 'Não apresentou erro'

        
        print("lista decode: ",decoder)
        BytesErro = listBytesErro[0]
        Framing = listFramig[0]
        self.socketsend(text, msg, decoder, BytesErro, Framing , bits)

    def socketRecive(self):
        HOST = 'localhost'
        PORT = 50000

        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        servidor.bind((HOST, PORT))

        servidor.listen()

        print("Aguardando conexão de um cliente")
        conn, ender = servidor.accept()

        print('Conectando em:', ender)
        try:
            while True:
                dados_recebidos = conn.recv(2048)
                if not dados_recebidos:
                    print('Fechando conexão')
                    conn.close()
                    break
                lista_recebida = json.loads(dados_recebidos.decode('utf-8'))
                print("Lista recebida:", lista_recebida)
                conn.sendall(str.encode('recebido'))
                self.aplicar(lista_recebida)

        finally:
            conn.close()



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
        crc = quadro[tamanho:]
        if 1 in crc:
            msg = 1
        else:
            msg = 0

        return original_quadro, msg

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

        return data_original, erro
    
teste = Aplicacao()
teste.socketRecive()