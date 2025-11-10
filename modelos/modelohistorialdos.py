import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

class ModeloHistorialdos:
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash", temperature: float = 0.7):
        load_dotenv()
        # Reviso si hay alguna de las dos API keys disponibles (GOOGLE o GEMINI)
        api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró GOOGLE_API_KEY o GEMINI_API_KEY en el entorno o .env")

        # Acá se inicializa el modelo de Gemini con LangChain
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key,
        )

        # Mensaje base del sistema (eso de que tenga la personalidad de un asistente)
        self._system_seed = "Eres un asistente útil y amigable."

        # Estructura del prompt: arranca con el sistema, sigue el historial y luego la pregunta
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._system_seed),
            MessagesPlaceholder("hist"),
            ("human", "{pregunta}")
        ])

        # Conecto el prompt con el modelo (esta es la cadena completa que se ejecuta)
        self.chain = self.prompt | self.llm

        self.reset()

    def reset(self):
        # Limpio el historial del chat (empieza vacío)
        self.historial: list = []

    def respond(self, pregunta: str) -> str:
        pregunta = (pregunta or "").strip()
        if not pregunta:
            return "Escribe un mensaje."

        try:
            # Le paso al modelo lo que llevo de historial y la nueva pregunta
            resp = self.chain.invoke({"hist": self.historial, "pregunta": pregunta})
            texto = (getattr(resp, "content", "") or "").strip()
        except Exception as e:
            return f"Error al generar respuesta: {e}"

        if not texto:
            texto = "No recibí texto del modelo (puede haber sido bloqueado por seguridad)."

        # Guardo la interacción (lo que mandó el usuario y la respuesta del modelo)
        self.historial.append(HumanMessage(content=pregunta))
        self.historial.append(AIMessage(content=texto))
        return texto
