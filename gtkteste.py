import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import socket
import json
import pickle

import numpy as np
import matplotlib.pyplot as plt

import Transmissor

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Networking Simulation")

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        self.text_entry = Gtk.Entry()
        self.box.pack_start(self.text_entry, True, True, 0)

        # Adicionando título aos grupos de botões de rádio
        self.box.pack_start(Gtk.Label("Codificação:"), True, True, 0)

        self.codification_radio = Gtk.RadioButton.new_with_label_from_widget(None, "NRZ Polar")
        self.box.pack_start(self.codification_radio, True, True, 0)

        self.codification_radio = Gtk.RadioButton.new_with_label_from_widget(self.codification_radio, "Manchester")
        self.box.pack_start(self.codification_radio, True, True, 0)

        self.codification_radio = Gtk.RadioButton.new_with_label_from_widget(self.codification_radio, "Bipolar")
        self.box.pack_start(self.codification_radio, True, True, 0)

        # Adicionando título aos grupos de botões de rádio
        self.box.pack_start(Gtk.Label("Enquadramento:"), True, True, 0)

        self.frame_radio = Gtk.RadioButton.new_with_label_from_widget(None, "Inserção de Byte")
        self.box.pack_start(self.frame_radio, True, True, 0)

        self.frame_radio = Gtk.RadioButton.new_with_label_from_widget(self.frame_radio, "Contagem de Caracteres")
        self.box.pack_start(self.frame_radio, True, True, 0)

        # Adicionando título aos grupos de botões de rádio
        self.box.pack_start(Gtk.Label("Detecção de Erro:"), True, True, 0)

        self.error_detection_radio = Gtk.RadioButton.new_with_label_from_widget(None, "Hamming")
        self.box.pack_start(self.error_detection_radio, True, True, 0)

        self.error_detection_radio = Gtk.RadioButton.new_with_label_from_widget(self.error_detection_radio, "CRC")
        self.box.pack_start(self.error_detection_radio, True, True, 0)

        self.error_detection_radio = Gtk.RadioButton.new_with_label_from_widget(self.error_detection_radio, "Bits de Paridade")
        self.box.pack_start(self.error_detection_radio, True, True, 0)

        # Adicionando checkboxes separados para modulação ASK e FSK
        self.ask_checkbox = Gtk.CheckButton("Modulação ASK")
        self.box.pack_start(self.ask_checkbox, True, True, 0)

        self.fsk_checkbox = Gtk.CheckButton("Modulação FSK")
        self.box.pack_start(self.fsk_checkbox, True, True, 0)

        self.execute_button = Gtk.Button(label="Executar")
        self.execute_button.connect("clicked", self.on_execute_button_clicked)
        self.box.pack_start(self.execute_button, True, True, 0)

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

        # Executar operações com base nas opções selecionadas
        result = self.perform_operations(text_input, selected_encoding, selected_framing, selected_error_detection, ask_selected, fsk_selected)

        # Exibir o resultado
        self.result_label.set_text(result)

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
    
    def socketRecived(self):
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

    def plotgrafics(self,Encoded,modulacaoASK, modulacaoFSK, encoding):
        plt.xaxis = np.arange(0, len(Encoded))
        plt.yaxis = np.array(Encoded)
        plt.step(plt.xaxis, plt.yaxis)
        plt.title(f'Sinal {encoding}')
        plt.show()
      
        if modulacaoASK:
            plt.plot(modulacaoASK[0], label='Sinal de ASK')
            plt.title('Sinal ASK')

            plt.xlabel('Amostras')
            plt.ylabel('Amplitude')
            plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição
            plt.show()
        if modulacaoFSK:
            plt.plot(modulacaoFSK[0], label='Sinal de FSK')
            plt.title('Sinal FSK')

            plt.xlabel('Amostras')
            plt.ylabel('Amplitude')
            plt.tight_layout()  # Ajusta automaticamente o layout para evitar sobreposição
            plt.show()


    def perform_operations(self, text_input, encoding, framing, error_detection, ask_selected, fsk_selected):
        # Implementar a lógica aqui usando as opções fornecidas e as classes
        # Chamar as funções apropriadas das classes CamadaFisica e CamadaEnlace
        modulation_result = []
        if ask_selected:
            modulation_result.append("Modulação ASK")
        if fsk_selected:
            modulation_result.append("Modulação FSK")


        trasnmissor = Transmissor.Aplicacao()
        bin_str, quadro, BytesErro, BytesEncoded, modulacaoASK, modulacaoFSK = trasnmissor.aplicar(text_input, encoding, framing, error_detection, modulation_result)
        result = f"Texto: {bin_str}\nEnquadramento: {quadro}\nDetecção de Erro: {BytesErro}\nCodificação: {BytesEncoded}"
    
        msg, listReceptora = self.socketRecived()

        self.plotgrafics(BytesEncoded, listReceptora[2], modulacaoASK, modulacaoFSK,encoding)

        return result + msg

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
