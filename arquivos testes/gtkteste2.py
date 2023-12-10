import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas

def encode_and_modulate(encoding, modulation, bit_stream):
    sig_size = len(bit_stream)
    signal = np.zeros(sig_size * 100)
    A = 1
    f = 1
    f1 = 1
    f2 = 2

    if modulation == "ASK":
        for i in range(sig_size):
            if bit_stream[i] == 1:
                for j in range(100):
                    signal[i * 100 + j] = A * np.sin(2 * np.pi * f * j / 100)
            else:
                for j in range(100):
                    signal[i * 100 + j] = 0

        return signal
    else:
        for i in range(sig_size):
            if bit_stream[i] == 1:
                for j in range(100):
                    signal[i * 100 + j] = A * np.sin(2 * np.pi * f2 * j / 100)
            else:
                for j in range(100):
                    signal[i * 100 + j] = A * np.sin(2 * np.pi * f1 * j / 100)

        return signal        


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Codificação e Modulação")
        self.set_default_size(800, 600)

        # Layout principal
        grid = Gtk.Grid()
        self.add(grid)

        # Campo de entrada
        self.entry = Gtk.Entry()
        self.entry.set_text("101010")  # Valor inicial
        grid.attach(self.entry, 0, 0, 1, 1)

        # Rádio botões para seleção de codificação
        encoding_label = Gtk.Label("Selecione a codificação:")
        grid.attach(encoding_label, 0, 1, 1, 1)

        self.nrz_polar_button = Gtk.RadioButton.new_with_label_from_widget(None, "NRZ Polar")
        self.manchester_button = Gtk.RadioButton.new_with_label_from_widget(self.nrz_polar_button, "Manchester")
        self.bipolar_button = Gtk.RadioButton.new_with_label_from_widget(self.nrz_polar_button, "Bipolar")

        grid.attach(self.nrz_polar_button, 0, 2, 1, 1)
        grid.attach(self.manchester_button, 0, 3, 1, 1)
        grid.attach(self.bipolar_button, 0, 4, 1, 1)

        # Checkbutton para seleção de modulação
        self.modulation_check = Gtk.CheckButton("Selecione a modulação (ASK/FSK)")
        grid.attach(self.modulation_check, 0, 5, 1, 1)

        # Botão para acionar a codificação e modulação
        encode_button = Gtk.Button.new_with_label("Codificar e Modular")
        encode_button.connect("clicked", self.on_encode_button_clicked)
        grid.attach(encode_button, 0, 6, 1, 1)

        # Adiciona a área de gráfico
        self.figure, self.ax = plt.subplots(figsize=(7, 5), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        grid.attach(self.canvas, 1, 0, 1, 7)

        # Inicializa o loop de eventos
        self.timeout_id = GObject.timeout_add(500, self.update_plot)

    def on_encode_button_clicked(self, button):
        data = self.entry.get_text()
        encoding = ""
        if self.nrz_polar_button.get_active():
            encoding = "NRZ Polar"
        elif self.manchester_button.get_active():
            encoding = "Manchester"
        elif self.bipolar_button.get_active():
            encoding = "Bipolar"

        modulation = "ASK" if self.modulation_check.get_active() else "FSK"

        self.signal = encode_and_modulate(encoding, modulation, list(map(int, data)))
        #print(f"Sinal gerado: {self.signal}")

    def update_plot(self):
        if hasattr(self, 'signal'):
            self.ax.clear()
            self.ax.plot(self.signal)
            self.canvas.draw()
        return True

win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

