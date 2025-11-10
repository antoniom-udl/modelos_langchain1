from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QPropertyAnimation
from modelos.modelogemini import ModeloGemini
from modelos.modelohistorialdos import ModeloHistorialdos
from modelos.modelohistoriallimitado import ModeloHistorialLimitado 

DEBUG = False  # pon True si quieres ver logs de depuración


class Load_ventana_modelos_basicos(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        # Cargo la UI desde el .ui (así no armo los widgets a mono)
        uic.loadUi("interfaces/Ventana_modelos_basicos.ui", self)

        # Ventana sin bordes y opacidad fija (look limpio)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)

        # Botón para cerrar la ventana (acción directa)
        self.boton_cerrar.clicked.connect(lambda: self.close())

        # Habilito arrastrar la ventana desde el frame superior
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        # Toggle del menú lateral
        self.boton_menu.clicked.connect(self.mover_menu)

        # Navegación por pestañas (voy por índice del stacked)
        self.boton_prompt.clicked.connect(self._ir_a_prompt)
        self.boton_memoria.clicked.connect(self._ir_a_memoria)
        self.boton_chat.clicked.connect(self._ir_a_chat)

        # Botones "Enviar" por pestaña (nombres tal cual en la UI)
        # Prompt
        self.boton_enviar.clicked.connect(self.ejecutar_prompt)
        if DEBUG: print("[DEBUG] conectado boton_enviar (Prompt) -> ejecutar_prompt")

        # Memoria
        self.boton_enviar_2.clicked.connect(self.ejecutar_memoria)
        if DEBUG: print("[DEBUG] conectado boton_enviar_2 (Memoria) -> ejecutar_memoria")

        # Chat (memoria limitada)
        self.boton_enviar_3.clicked.connect(self.ejecutar_chat)
        if DEBUG: print("[DEBUG] conectado boton_enviar_3 (Chat) -> ejecutar_chat")

        # Instancias diferidas (se crean cuando se usan)
        self._gemini = None                    # Prompt
        self._memoria_model = None             # Memoria persistente
        self._chat_model_limited = None        # Chat con 5 turnos de memoria

    # NAVEGACIÓN 
    def _ir_a_prompt(self):
        i_prompt = self.stackedWidget.indexOf(self.page_prompt)
        if DEBUG:
            before = self.stackedWidget.currentIndex()
            print(f"[DEBUG] boton_prompt: before={before} -> promptIndex={i_prompt}")
        self.stackedWidget.setCurrentIndex(i_prompt)

    def _ir_a_memoria(self):
        i_mem = self.stackedWidget.indexOf(self.page_memoria)
        if DEBUG:
            before = self.stackedWidget.currentIndex()
            print(f"[DEBUG] boton_memoria: before={before} -> memoriaIndex={i_mem}")
        self.stackedWidget.setCurrentIndex(i_mem)

    def _ir_a_chat(self):
        i_chat = self.stackedWidget.indexOf(self.page_chat)
        if DEBUG:
            before = self.stackedWidget.currentIndex()
            print(f"[DEBUG] boton_chat: before={before} -> chatIndex={i_chat}")
        self.stackedWidget.setCurrentIndex(i_chat)

    # PROMPT 
    def ejecutar_prompt(self):
        prompt = self.input_prompt.text().strip()
        salida = self.output_response

        if not prompt:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Escribe un prompt primero.")
            return

        self._bloquear_boton(self.boton_enviar, "Enviando...")

        try:
            # Creo el modelo solo la primera vez (evito reinstanciar)
            if self._gemini is None:
                self._gemini = ModeloGemini()

            # Pido texto a Gemini y lo mando a la salida
            respuesta = self._gemini.generar(prompt)
            salida.setPlainText(respuesta)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")
        finally:
            self._desbloquear_boton(self.boton_enviar)

    # MEMORIA (persistente)
    def _get_memoria_model(self):
        # Devuelvo la instancia (si no existe, la creo aquí)
        if self._memoria_model is None:
            if DEBUG: print("[DEBUG] creando instancia de ModeloHistorialdos")
            self._memoria_model = ModeloHistorialdos()
        return self._memoria_model

    def ejecutar_memoria(self):
        if DEBUG: print("[DEBUG] ejecutar_memoria()")

        mensaje = self.input_prompt_2.text().strip()
        salida = self.output_response_2

        if not mensaje:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Escribe un mensaje primero.")
            return

        self._bloquear_boton(self.boton_enviar_2, "Enviando...")

        try:
            # Uso el modelo con historial completo (no se resetea solo)
            modelo = self._get_memoria_model()
            respuesta = modelo.respond(mensaje)
            if DEBUG: print(f"[DEBUG] respuesta (memoria): {respuesta!r}")
            if not respuesta:
                respuesta = "No se recibió respuesta del modelo."

            # Voy acumulando conversación en el text box
            previo = salida.toPlainText()
            bloque = f"Tú: {mensaje}\nBot: {respuesta}\n"
            salida.setPlainText((previo + "\n" + bloque).strip())
            self.input_prompt_2.clear()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")
            if DEBUG: print("[DEBUG] Error en ejecutar_memoria:", e)
        finally:
            self._desbloquear_boton(self.boton_enviar_2)

    # CHAT (memoria limitada a 5)
    def _get_chat_model(self):
        # Devuelvo la instancia del chat con límite (si no existe, la creo)
        if self._chat_model_limited is None:
            if DEBUG: print("[DEBUG] creando instancia de ModeloHistorialLimitado(max_turns=5)")
            # Si alguna vez quieres otro límite, pasa max_turns= y el valor que ahora quieras
            self._chat_model_limited = ModeloHistorialLimitado(max_turns=5)
        return self._chat_model_limited

    def ejecutar_chat(self):
        if DEBUG: print("[DEBUG] ejecutar_chat()")

        mensaje = self.input_prompt_3.text().strip()
        salida = self.output_response_3

        if not mensaje:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Escribe un mensaje primero.")
            return

        self._bloquear_boton(self.boton_enviar_3, "Enviando...")

        try:
            # Uso el modelo con memoria que se reinicia al llegar al límite
            modelo = self._get_chat_model()
            respuesta = modelo.respond(mensaje)
            if DEBUG: print(f"[DEBUG] respuesta (chat limitado): {respuesta!r}")
            if not respuesta:
                respuesta = "No se recibió respuesta del modelo."

            # Acumulo el chat en el cuadro de salida de esta pestaña
            previo = salida.toPlainText()
            bloque = f"Tú: {mensaje}\nBot: {respuesta}\n"
            salida.setPlainText((previo + "\n" + bloque).strip())
            self.input_prompt_3.clear()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{e}")
            if DEBUG: print("[DEBUG] Error en ejecutar_chat:", e)
        finally:
            self._desbloquear_boton(self.boton_enviar_3)

    # UTILIDADES DE UI
    def _bloquear_boton(self, btn, texto="Enviando..."):
        # Evito doble clic mientras se procesa (deshabilito y cambio texto)
        if btn:
            btn.setEnabled(False)
            btn.setText(texto)

    def _desbloquear_boton(self, btn):
        # Vuelvo el botón a su estado normal
        if btn:
            btn.setEnabled(True)
            btn.setText("Enviar")

    def mousePressEvent(self, event):
        # Guardo posición global del clic para poder arrastrar luego
        self.clickPosition = event.globalPos()

    def mover_ventana(self, event):
        # Arrastre manual cuando no está maximizada (desde la barra superior)
        if not self.isMaximized():
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.clickPosition)
                self.clickPosition = event.globalPos()
                event.accept()

        # Maximizar si pego al borde superior; si no, volver a normal
        if event.globalPos().y() <= 20:
            self.showMaximized()
        else:
            self.showNormal()

    def mover_menu(self):
        # Toggle del panel lateral (0 ↔ 200) y texto del botón
        width = self.frame_lateral.width()
        normal = 0
        if width == 0:
            extender = 200
            self.boton_menu.setText("Menú")
        else:
            extender = normal
            self.boton_menu.setText("")

        # Animación del ancho del panel lateral
        self.animacion = QtCore.QPropertyAnimation(self.frame_lateral, b"minimumWidth")
        self.animacion.setDuration(300)
        self.animacion.setStartValue(width)
        self.animacion.setEndValue(extender)
        self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animacion.start()

        # Acompaño con animación del botón del menú (mismo ancho)
        self.animacionb = QPropertyAnimation(self.boton_menu, b"minimumWidth")
        self.animacionb.setStartValue(width)
        self.animacionb.setEndValue(extender)
        self.animacionb.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animacionb.start()
