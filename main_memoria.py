from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# Cargar API Key de Gemini desde .env
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
# Inicializar Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # o gemini-pro, según tu API
    temperature=0.7
)
# Configurar memoria
memory = ConversationBufferMemory()

# Crear la cadena de conversación
conv = ConversationChain(llm=llm, memory=memory)

# Interactuar
print(conv.run("Hola, ¿cómo estás?"))
#print(conv.run("Me llamo Alejandro."))
print(conv.run("¿Recuerdas mi nombre?"))