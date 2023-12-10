import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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

    def perform_operations(self, text_input, encoding, framing, error_detection, ask_selected, fsk_selected):
        # Implementar a lógica aqui usando as opções fornecidas e as classes
        # Chamar as funções apropriadas das classes CamadaFisica e CamadaEnlace
        modulation_result = []
        if ask_selected:
            modulation_result.append("Modulação ASK")
        if fsk_selected:
            modulation_result.append("Modulação FSK")


        trasnmissor = Transmissor.Aplicacao()
        bin_str, quadro, BytesErro, BytesEncoded = trasnmissor.aplicar(text_input, encoding, framing, error_detection, modulation_result)
        result = f"Texto: {bin_str}\nEnquadramento: {quadro}\nDetecção de Erro: {BytesErro}\nCodificação: {BytesEncoded}"
        return result

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
