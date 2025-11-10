from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QPropertyAnimation
from llmchain_v1 import run_llmchain  # función que ejecuta Gemini con LangChain

UI_PATH = "interfaces/ventana_modelo_ochos.ui"
DEBUG = False


class Load_ventana_ocho(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        # Cargar la UI desde el .ui (me ahorro armar widgets a mano)
        uic.loadUi(UI_PATH, self)

        # Ventana sin bordes y con opacidad fija (para look limpio)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1.0)

        # Cachar referencias de los contenedores clave (me ubico en la UI)
        self.frame_central = self._w("frame_central")
        self.frame_lateral = self._w("frame_lateral")
        self.frame_paginas = self._w("frame_paginas")
        self.frame_superior = self._w("frame_superior")
        self.stackedWidget = self._w("stackedWidget")

        # Botones de la barra de arriba (menú y cerrar)
        self.boton_menu = self._w("boton_menu")
        self.boton_cerrar = self._w("boton_cerrar")

        if self.boton_cerrar:
            self.boton_cerrar.clicked.connect(self.close)
        if self.frame_superior:
            self.frame_superior.mouseMoveEvent = self.mover_ventana
        if self.boton_menu:
            self.boton_menu.clicked.connect(self.mover_menu)

        # Botones laterales 1–8 (para saltar entre páginas)
        self.boton_1 = self._w("boton_1")
        self.boton_2 = self._w("boton_2")
        self.boton_3 = self._w("boton_3")
        self.boton_4 = self._w("boton_4")
        self.boton_5 = self._w("boton_5")
        self.boton_6 = self._w("boton_6")
        self.boton_7 = self._w("boton_7")
        self.boton_8 = self._w("boton_8")

        # Enlazar widgets de cada página (inputs, botones y salidas)
        for i in range(1, 9):
            setattr(self, f"page_{i}", self._w(f"page_{i}"))
            setattr(self, f"input_prompt_{i}", self._w(f"input_prompt_{i}" if i > 1 else "input_prompt"))
            setattr(self, f"boton_enviar_{i}", self._w(f"boton_enviar_{i}" if i > 1 else "boton_enviar"))
            setattr(self, f"output_response_{i}", self._w(f"output_response_{i}" if i > 1 else "output_response"))
            setattr(self, f"label_{i}", self._w(f"label_{i+1}" if i > 1 else "label_2"))

        # Conecto los botones laterales para navegar el stacked
        self._conectar_navegacion()

        # Página 1: hook para mandar el prompt al LLM
        if self.boton_enviar_1:
            self.boton_enviar_1.clicked.connect(self._ejecutar_llmchain_page1)

        # Arranco mostrando la primera página
        if self.stackedWidget:
            self.stackedWidget.setCurrentIndex(0)

        # Estado inicial para animaciones y drag
        self.clickPosition = None
        self.animacion = None
        self.animacionb = None

        if DEBUG and self.stackedWidget:
            print("[DEBUG] Ventana LangChain cargada correctamente.")
            print("[DEBUG] Páginas detectadas:",
                  [self.stackedWidget.widget(i).objectName() for i in range(self.stackedWidget.count())])


    #LÓGICA DE LA PÁGINA 1 (LangChain LLMChain) 

    def _ejecutar_llmchain_page1(self):
        #Lee el texto de input_prompt_1, ejecuta Gemini y muestra la respuesta.
        if not self.input_prompt_1 or not self.output_response_1:
            QtWidgets.QMessageBox.critical(self, "Error", "No se encontraron los widgets de la página 1.")
            return

        tema = (self.input_prompt_1.text() or "").strip()
        if not tema:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Escribe un tema primero.")
            return

        self._bloquear_boton(self.boton_enviar_1, "Enviando...")

        try:
            texto = run_llmchain(tema)
            # Armo el bloque con lo que mandé y lo que regresó el bot (voy acumulando)
            texto_prev = self.output_response_1.toPlainText().strip()
            bloque = f"Tú: {tema}\nBot: {texto}\n"
            self.output_response_1.setPlainText((texto_prev + "\n" + bloque).strip())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")
        finally:
            self._desbloquear_boton(self.boton_enviar_1)
            if self.input_prompt_1:
                self.input_prompt_1.clear()
                self.input_prompt_1.setFocus()


    #NAVEGACIÓN ENTRE PÁGINAS

    def _conectar_navegacion(self):
        if not self.stackedWidget:
            return

        # Mapa botón índice del stacked (atajo rápido)
        mapa = {
            "boton_1": 0,
            "boton_2": 1,
            "boton_3": 2,
            "boton_4": 3,
            "boton_5": 4,
            "boton_6": 5,
            "boton_7": 6,
            "boton_8": 7
        }

        # Conecto cada botón a su página correspondiente
        for nombre_btn, idx in mapa.items():
            btn = self._w(nombre_btn)
            if btn and idx < self.stackedWidget.count():
                btn.clicked.connect(lambda _, i=idx: self.stackedWidget.setCurrentIndex(i))


    #UTILIDADES                

    def _w(self, name):
        """Devuelve un widget si existe, o None si no."""
        # Buscar el widget por atributo y si no, por nombre en el árbol
        obj = getattr(self, name, None)
        if obj is None:
            obj = self.findChild(QtCore.QObject, name)
        return obj

    def _bloquear_boton(self, btn, texto="Enviando..."):
        # Deshabilito y cambio el texto para evitar doble clic mientras corre
        if btn:
            btn.setEnabled(False)
            btn.setText(texto)

    def _desbloquear_boton(self, btn):
        # Reactivo el botón y regreso el texto normal
        if btn:
            btn.setEnabled(True)
            btn.setText("Enviar")


    #ANIMACIONES / MOVIMIENTO DE VENTANA 
    def mousePressEvent(self, event):
        # Guardo la posición global para calcular el drag
        self.clickPosition = event.globalPos()

    def mover_ventana(self, event):
        # Permite arrastrar la ventana desde la barra superior (cuando no está maximizada)
        if not self.isMaximized() and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.clickPosition)
            self.clickPosition = event.globalPos()
            event.accept()

        # Auto-maximiza si llego al borde superior, si no vuelve a normal
        if event.globalPos().y() <= 20:
            self.showMaximized()
        else:
            self.showNormal()

    def mover_menu(self):
        """Animación para mostrar u ocultar el menú lateral."""
        if not self.frame_lateral:
            return

        # Si está en 0 lo extiendo a 200, si no, lo cierro (toggle)
        width = self.frame_lateral.width()
        extender = 200 if width == 0 else 0

        # Animación del panel lateral (suavizado con InOutQuart)
        self.animacion = QPropertyAnimation(self.frame_lateral, b"minimumWidth")
        self.animacion.setDuration(300)
        self.animacion.setStartValue(width)
        self.animacion.setEndValue(extender)
        self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animacion.start()

        # Sincronizo el ancho del botón del menú para que acompañe la animación
        if self.boton_menu:
            self.animacionb = QPropertyAnimation(self.boton_menu, b"minimumWidth")
            self.animacionb.setDuration(300)
            self.animacionb.setStartValue(width)
            self.animacionb.setEndValue(extender)
            self.animacionb.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animacionb.start()
