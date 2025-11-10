#pip install langchain langchain-google-genai google-generativeai
#pip install python-dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os


# Cargar variables del archivo .env
load_dotenv()

# Obtener la clave API desde las variables de entorno
api_key = os.getenv("GOOGLE_API_KEY")

# Verifica que esté cargada
if not api_key:
    raise ValueError("La variable GOOGLE_API_KEY no está definida en el archivo .env")

# Crear el modelo LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=api_key  # Puedes pasarla directamente
)

# Memoria para el historial de conversación
memory = ConversationBufferMemory()

# Cadena de conversación
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Bucle de conversación
print("Chat con Gemini (LangChain + .env). Escribe 'salir' para terminar.\n")
while True:
    mensaje = input("Tú: ")
    if mensaje.lower() in ["salir", "exit"]:
        break

    respuesta = conversation.predict(input=mensaje)
    print("Gemini:", respuesta)