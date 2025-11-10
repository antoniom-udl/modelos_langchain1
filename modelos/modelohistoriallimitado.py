import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

class ModeloHistorialLimitado:
    #Chat con memoria limitada: después de `max_turns` mensajes de USUARIO,se reinicia el historial (olvida todo lo anterior menos lo de que es un asistente util y amigable).
    
    def __init__(self, api_key: str | None = None, max_turns: int = 5,
                 model: str = "gemini-2.5-flash", temperature: float = 0.7):
        load_dotenv()
        api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró GOOGLE_API_KEY o GEMINI_API_KEY")

        # Acá se inicializa el modelo de Google con la API key y config básica
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key,
        )

        self.max_turns = max(1, int(max_turns))  # mínimo 1, por si acaso

        # Mensaje base que siempre va al principio del chat
        self._system_seed = "Eres un asistente útil y amigable."

        # Armo el prompt del chat con el historial y la pregunta actual
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._system_seed),
            MessagesPlaceholder("hist"),
            ("human", "{pregunta}"),
        ])

        # Cadena que conecta el prompt con el modelo (flujo completo)
        self.chain = self.prompt | self.llm

        self.reset()

    def reset(self):
        # Reinicio el historial del chat (limpio todo)
        self.historial: list = []

    def _count_user_turns(self) -> int:
        # Contador para ver cuántos mensajes mandó el usuario hasta ahora
        return sum(isinstance(m, HumanMessage) for m in self.historial)

    def respond(self, pregunta: str) -> str:
        pregunta = (pregunta or "").strip()
        if not pregunta:
            return "Escribe un mensaje."

        # Calculo cuántos turnos de USUARIO hay en el historial y aplico el límite
        if self._count_user_turns() >= self.max_turns:
            self.reset()

        try:
            # Le paso el historial y la nueva pregunta al modelo
            resp = self.chain.invoke({"hist": self.historial, "pregunta": pregunta})
            texto = (getattr(resp, "content", "") or "").strip()
        except Exception as e:
            return f"Error al generar respuesta: {e}"

        if not texto:
            texto = "No recibí texto del modelo (puede haber sido bloqueado por seguridad)."

        # Guardo lo que dijo el usuario y la respuesta del modelo
        self.historial.append(HumanMessage(content=pregunta))
        self.historial.append(AIMessage(content=texto))

        return texto
