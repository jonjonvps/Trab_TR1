# Universidade de Brasilia
# Departamento de Ciencia da Computacao
# Disciplina de Teleinformatica e Redes 1
# Professor Marcelo Antonio Marotta
# Trabalho final da disciplina
# Alunos :  Andre Cassio Barros de Souza    160111943
#           Andrey Galvao Mendes            180097911
#           Davi Oliveira Fuzo              202024446
#           Joao Victor Pinheiro de Souza   180103407

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import socket
import json
import pickle

import numpy as np
import matplotlib.pyplot as plt

import Transmissor
import threading

class MyWindow(Gtk.Window):
    def __init__(self):

        self.HOST = 'localhost'
        self.PORT = 50000
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



        Gtk.Window.__init__(self, title="Simulador de Transmissor")

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        # Input field para a mensagem a ser transmitida
        self.text_entry = Gtk.Entry()
        self.box.pack_start(self.text_entry, True, True, 0)

        # Adicionando título aos grupos de botões de rádio
        
        self.codification_label = Gtk.Label(label="Codificação:")
        self.box.pack_start(self.codification_label, True, True, 0)
        #self.box.pack_start(Gtk.Label("Codificação:"), True, True, 0)

        self.codification_radio = Gtk.RadioButton.new_with_label_from_widget(None, "NRZ Polar")
        self.box.pack_start(self.codification_radio, True, True, 0)

        self.codification_radio = Gtk.RadioButton.new_with_label_from_widget(self.codification_radio, "Manchester")
        self.box.pack_start(self.codification_radio, True, True, 0)

        self.codification_radio = Gtk.RadioButton.new_with_label_from_widget(self.codification_radio, "Bipolar")
        self.box.pack_start(self.codification_radio, True, True, 0)

        # Adicionando título aos grupos de botões de rádio
        self.frame_label = Gtk.Label(label="Enquadramento:")
        self.box.pack_start(self.frame_label, True, True, 0)
        #self.box.pack_start(Gtk.Label("Enquadramento:"), True, True, 0)

        self.frame_radio = Gtk.RadioButton.new_with_label_from_widget(None, "Inserção de Byte")
        self.box.pack_start(self.frame_radio, True, True, 0)

        self.frame_radio = Gtk.RadioButton.new_with_label_from_widget(self.frame_radio, "Contagem de Caracteres")
        self.box.pack_start(self.frame_radio, True, True, 0)

        # Adicionando título aos grupos de botões de rádio
        self.error_detection_label = Gtk.Label(label="Detecção de Erro:")
        self.box.pack_start(self.error_detection_label, True, True, 0)
        #self.box.pack_start(Gtk.Label("Detecção de Erro:"), True, True, 0)

        self.error_detection_radio = Gtk.RadioButton.new_with_label_from_widget(None, "Hamming")
        self.box.pack_start(self.error_detection_radio, True, True, 0)

        self.error_detection_radio = Gtk.RadioButton.new_with_label_from_widget(self.error_detection_radio, "CRC")
        self.box.pack_start(self.error_detection_radio, True, True, 0)

        self.error_detection_radio = Gtk.RadioButton.new_with_label_from_widget(self.error_detection_radio, "Bits de Paridade")
        self.box.pack_start(self.error_detection_radio, True, True, 0)

        # Adicionando checkboxes separados para modulação ASK e FSK
        self.ask_checkbox = Gtk.CheckButton(label="Modulação ASK")
        self.box.pack_start(self.ask_checkbox, True, True, 0)

        self.fsk_checkbox = Gtk.CheckButton(label="Modulação FSK")
        self.box.pack_start(self.fsk_checkbox, True, True, 0)

        self.erro_checkbox = Gtk.CheckButton(label="Adicionar erro")
        self.box.pack_start(self.erro_checkbox, True, True, 0)


        # box para conectar ao servidor

        self.connect_to_server_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.box.pack_start(self.connect_to_server_box, True, True, 0)

        self.connect_to_server_button = Gtk.Button(label="Conectar ao servidor")
        self.connect_to_server_button.connect("clicked", self.try_connect_to_server)
        self.connect_to_server_box.pack_start(self.connect_to_server_button, True, True, 0)

        self.connecting_to_server_spinner = Gtk.Spinner()
        self.connect_to_server_box.pack_start(self.connecting_to_server_spinner, True, True, 0)
        self.connecting_to_server_spinner.set_visible(False)

        self.connecting_to_server_result_label = Gtk.Label()
        self.connect_to_server_box.pack_start(self.connecting_to_server_result_label, True, True, 0)
        self.connecting_to_server_result_label.set_visible(False)


        self.execute_button = Gtk.Button(label="Enviar")
        self.execute_button.connect("clicked", self.on_execute_button_clicked)
        self.execute_button.set_sensitive(False)
        self.box.pack_start(self.execute_button, True, True, 0)



        # Adicionando campos de output da transmissao
        self.result_label = Gtk.Label()
        self.box.pack_start(self.result_label, True, True, 0)

    def on_execute_button_clicked(self, widget):
        text_input = self.text_entry.get_text()

        # Obter opções selecionadas
        selected_encoding = self.get_selected_option(self.box, "Codificação:")
        selected_framing = self.get_selected_option(self.box, "Enquadramento:")
        selected_error_detection = self.get_selected_option(self.box, "Detecção de Erro:")
        ask_selected = self.ask_checkbox.get_active()
        fsk_selected = self.fsk_checkbox.get_active()
        erro_selected = self.erro_checkbox.get_active()

        # Executar operações com base nas opções selecionadas
        result = self.perform_operations(text_input, selected_encoding, selected_framing, selected_error_detection, ask_selected, fsk_selected, erro_selected)

        # Exibir o resultado <= resultado agora eh mostrado no perform_operations
        # self.show_transmission_results(result)
        #self.result_label.set_text(result)

    def get_selected_option(self, container, group_label):
        # Encontrar o grupo de botões de rádio com o título fornecido
        for widget in container.get_children():
            if isinstance(widget, Gtk.Label) and widget.get_text() == group_label:
                group_start = container.get_children().index(widget) + 1
                group_end = group_start
                for i in range(group_start, len(container.get_children())):
                    if isinstance(container.get_children()[i], Gtk.Label):
                        break
                    group_end += 1
                # Verificar qual opção foi selecionada no grupo de botões de rádio
                for i in range(group_start, group_end):
                    if container.get_children()[i].get_active():
                        return container.get_children()[i].get_label()
        return None

    def data_received(self,data):
        msg = f"\n\nReceptora\n\nDecodificação: {data[2]}\nDetecção de erro: {data[1]} {data[3]}\nEnquadramento: {data[4]}\nTexto em Binario: {data[5]}\nMensagem: {data[0]}"
        return msg
    
    def socketReceived(self):
        HOST = 'localhost'
        PORT = 20000

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
                print("Lista recebida GTK:", lista_recebida)
                conn.sendall(str.encode('recebido'))
                msg = self.data_received(lista_recebida)

        finally:
            conn.close()

        return msg, lista_recebida

    def plot_graphics(self, Encoded, modulacaoASK, modulacaoFSK, encoding):
        plt.xaxis = np.arange(0, len(Encoded))
        plt.yaxis = np.array(Encoded)
        plt.xlabel('Tempo')
        plt.ylabel('Amplitude (V)')
        plt.step(plt.xaxis, plt.yaxis)
        plt.title(f'Sinal {encoding}')
        plt.show()
      
        if modulacaoASK:
            plt.plot(modulacaoASK[0], label='Sinal de ASK')
            plt.title('Sinal ASK')

            plt.xlabel('Tempo')
            plt.ylabel('Amplitude (V)')
            plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição
            plt.show()
        if modulacaoFSK:
            plt.plot(modulacaoFSK[0], label='Sinal de FSK')
            plt.title('Sinal FSK')

            plt.xlabel('Tempo')
            plt.ylabel('Amplitude (V)')
            plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição
            plt.show()


    def perform_operations(self, text_input, encoding, framing, error_detection, ask_selected, fsk_selected, erro_selected):
        # Implementar a lógica aqui usando as opções fornecidas e as classes
        # Chamar as funções apropriadas das classes CamadaFisica e CamadaEnlace
        modulation_result = []
        if ask_selected:
            modulation_result.append("Modulação ASK")
        if fsk_selected:
            modulation_result.append("Modulação FSK")


        transmissor = Transmissor.Aplicacao()
        bin_str, quadro, BytesErro, BytesEncoded, modulacaoASK, modulacaoFSK = transmissor.aplicar(text_input, encoding, framing, error_detection, modulation_result, erro_selected)
        result = f"Texto: {bin_str}\nEnquadramento: {quadro}\nDetecção de Erro: {BytesErro}\nCodificação: {BytesEncoded}"

        #msg, listReceptora = self.socketReceived()
        # data, encoding, framing, error_detection

        
        self.send_data_to_server(BytesEncoded, encoding, framing, error_detection)

        self.show_transmission_results(result, BytesEncoded[0], modulacaoASK, modulacaoFSK, encoding)

        #return result + msg

        return result
    
    def show_transmission_results(self, result_text, BytesEncoded, modulacaoASK, modulacaoFSK, encoding):
        self.result_label.set_text(result_text)
        self.plot_graphics(BytesEncoded, modulacaoASK, modulacaoFSK, encoding)


    def try_connect_to_server(self, widget):

        # desabilitar botao de tentar conectar.
        self.connect_to_server_button.set_sensitive(False)
        self.connecting_to_server_result_label.set_visible(False)

        # mostrar e iniciar spinner
        self.connecting_to_server_spinner.set_visible(True)
        self.connecting_to_server_spinner.start()

        connection_accept_thread = threading.Thread(target=self.connect_to_server_loop)
        connection_accept_thread.daemon = True
        connection_accept_thread.start()


    def connect_to_server_loop(self):
        print("tentando conectar ao servidor")
        try:
            self.client.connect((self.HOST,self.PORT))
            self.show_connection_success_ui()
            
        except socket.error:
            self.show_connection_fail_ui()
            

    def show_connection_success_ui(self):
        print("conexao estabelecida")
        self.connecting_to_server_spinner.stop()
        self.connecting_to_server_spinner.set_visible(False)

        self.connecting_to_server_result_label.set_text("Conectado!")
        self.connecting_to_server_result_label.set_visible(True)

        self.execute_button.set_sensitive(True)

    def show_connection_fail_ui(self):
        print("conexao falhou")
        self.connecting_to_server_spinner.stop()
        self.connecting_to_server_spinner.set_visible(False)
            
        self.connecting_to_server_result_label.set_text("Erro na conexao!")
        self.connecting_to_server_result_label.set_visible(True)

        self.connect_to_server_button.set_sensitive(True)
        self.execute_button.set_sensitive(False)

    def send_data_to_server(self, data, encoding, framing, error_detection):
        print("mandando mensagem para o servidor")
        data.extend((encoding, framing, error_detection))

        dados_a_enviar = json.dumps(data)
        self.client.sendall(dados_a_enviar.encode('utf-8'))

        wait_data_from_server_thread = threading.Thread(target=self.wait_data_from_server)
        wait_data_from_server_thread.daemon = True
        wait_data_from_server_thread.start()


    def wait_data_from_server(self):
        menssage = self.client.recv(2048)
        print('Mensagem servidor Socket: ', menssage.decode())

        # finalizar conexao?
        print("Finalizando conexao com servidor.")
        self.client.close()


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.set_default_size(500, 400)
win.show_all()
Gtk.main()
