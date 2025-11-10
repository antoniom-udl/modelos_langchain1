from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os, logging

# Desactivo los logs de gRPC y Google (para mantener limpio el output)
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_CPP_VERBOSITY"] = "NONE"
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("grpc").setLevel(logging.ERROR)

_chain = None  # guardo la cadena para reutilizarla después (cache interno)

def _get_chain():
    global _chain
    if _chain is not None:
        return _chain  # si ya la tengo creada, la devuelvo directo

    # Cargar la API key desde el .env
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("No se encontró GOOGLE_API_KEY. Revisa tu archivo .env")

    # Configuro el modelo de Gemini con LangChain
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        google_api_key=api_key,
    )

    # Armo el prompt base (le paso el tema al modelo para que lo explique)
    prompt = PromptTemplate.from_template(
        "Explícale a un estudiante universitario como si fueras un profesor experto en el tema {tema}."
    )

    # Conecto el prompt con el modelo (flujo final)
    _chain = prompt | llm
    return _chain

def run_llmchain(tema: str) -> str:
    # Limpio el texto por si viene vacío o con espacios
    tema = (tema or "").strip()
    if not tema:
        return "Escribe un tema válido."

    # Ejecuto la cadena con el tema y obtengo la respuesta
    chain = _get_chain()
    resp = chain.invoke({"tema": tema})

    # Devuelvo el texto limpio o aviso si no hay contenido
    return (getattr(resp, "content", "") or "").strip() or "Sin contenido devuelto."
