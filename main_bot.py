from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# Cargar API Key
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Inicializar modelo
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# Crear memoria para mantener la conversación
memory = ConversationBufferMemory(memory_key="chat_history")

# Plantilla de prompt
prompt = PromptTemplate(
    input_variables=["input", "chat_history"],
    template="""
Eres un asistente educativo de la institución, su página es www.universidaddeleon.edu.mx. Responde las preguntas de los estudiantes de forma clara.
Historial de conversación:
{chat_history}

Pregunta del estudiante: {input}
Respuesta:
"""
)

# Crear la cadena de conversación
chatbot = ConversationChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)

# Interfaz básica por consola
print("¡Chatbot educativo activo! Escribe 'salir' para terminar.")
while True:
    pregunta = input("Tú: ")
    if pregunta.lower() == "salir":
        break
    respuesta = chatbot.run(pregunta)
    print("Bot:", respuesta)