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

import recep1

import socket
import json
import pickle

import threading

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Simulador de Receptor")

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        self.start_client_button = Gtk.Button(label="Iniciar Servidor")
        self.start_client_button.connect("clicked", self.start_client)
        self.box.pack_start(self.start_client_button, True, True, 0)

        # Adicionando campos de output da transmissao
        self.main_state_label = Gtk.Label()
        self.box.pack_start(self.main_state_label, True, True, 0)

        self.result_spinner = Gtk.Spinner()
        self.box.pack_start(self.result_spinner, True, True, 0)

        self.decode_result_label = Gtk.Label()
        self.box.pack_start(self.decode_result_label, True, True, 0)

        self.client = recep1.Aplicacao()


        # Hard coded host and port, maybe change to input fields

        HOST = 'localhost'
        PORT = 50000
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server.bind((HOST, PORT))


    def start_client(self, widget):

        self.show_starting_client_ui()

        self.server.listen()

        self.show_listening_connection_ui()

        connection_accept_thread = threading.Thread(target=self.client_connection_accept_loop)
        connection_accept_thread.daemon = True
        connection_accept_thread.start()

    def client_connection_accept_loop(self):
        print("Aguardando conexão de um cliente")
        conn, ender = self.server.accept()

        print('Conectando em:', ender)
        self.show_client_connected_ui(ender)
        try:
            while True:
                dados_recebidos = conn.recv(2048)
                if not dados_recebidos:
                    print('Fechando conexão, dados nao recebidos')
                    conn.close()
                    break
                lista_recebida = json.loads(dados_recebidos.decode('utf-8'))
                print("Lista recebida:", lista_recebida)
                conn.sendall(str.encode('recebido'))

                text, msg, decoder, BytesErro, Framing, bits = self.client.aplicar(lista_recebida)
                self.show_decode_result_ui(text, msg, decoder, BytesErro, Framing, bits)

        finally:
            conn.close()

    
    def show_starting_client_ui(self):
        self.main_state_label.set_text("Iniciando cliente...")
        self.start_client_button.set_visible(False)


    def show_listening_connection_ui(self):
        self.main_state_label.set_text("Esperando conexao...")
        self.result_spinner.start()

    def show_client_connected_ui(self, connected_client_address):
        self.result_spinner.stop()
        self.result_spinner.set_visible(False)
        result_text = f"Conectado a {connected_client_address}"
        self.main_state_label.set_text(result_text)

    

    def show_decode_result_ui(self, text, msg, decoder, BytesErro, Framing, bits):
        result_text = f"Mensagem recebida.\nTexto: {text}\nEnquadramento: {Framing}\nDeteccao de Erro: {BytesErro}\nResultado de deteccao de erro: {msg}\nDecodificacao: {decoder}\nBits: {bits}"
        self.decode_result_label.set_text(result_text)



win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.set_default_size(500, 400)
win.show_all()
Gtk.main()
