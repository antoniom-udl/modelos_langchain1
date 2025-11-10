#pip install langchain-google-genai google-generativeai python-dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar el modelo
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# Realizar una consulta
respuesta = llm.invoke("Escribe un poema sobre la inteligencia artificial.")
print(respuesta.content)