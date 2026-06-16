"""
A2A Server — Experto en instrumentos musicales con búsqueda web
http://localhost:9999
"""

import os
import uvicorn
import httpx
from dotenv import load_dotenv

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill

from agent_framework import Agent
from agent_framework.a2a import A2AExecutor
from agent_framework.openai import AzureOpenAIChatClient

from starlette.applications import Starlette

load_dotenv()

# ── Tool: búsqueda especializada en instrumentos musicales ──────────────────

def buscar_instrumentos(consulta: str) -> str:
    """Busca en internet información sobre instrumentos musicales."""
    params = {
        "q": f"instrumento musical {consulta}",
        "api_key": os.environ["SERPAPI_KEY"],
        "num": 5,
    }
    response = httpx.get("https://serpapi.com/search", params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    resultados = []
    for r in data.get("organic_results", [])[:5]:
        titulo = r.get("title", "Sin título")
        snippet = r.get("snippet", "")
        link = r.get("link", "")
        resultados.append(f"- {titulo}: {snippet} ({link})")

    return "\n".join(resultados) if resultados else "Sin resultados."


# ── AgentCard ───────────────────────────────────────────────────────────────

agent_card = AgentCard(
    name="Experto en Instrumentos Musicales",
    description="Chat especializado en instrumentos musicales. Busca info actualizada en internet.",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[
        AgentInterface(url="http://localhost:9999/", protocol_binding="JSONRPC"),
    ],
    skills=[
        AgentSkill(
            id="instrument_search",
            name="Búsqueda de Instrumentos",
            description="Busca información actualizada sobre instrumentos musicales.",
            tags=["música", "instrumentos", "búsqueda"],
            examples=["¿Cuánto cuesta una guitarra flamenca?", "Diferencias entre violín y viola"],
        )
    ],
)

# ── Agente ──────────────────────────────────────────────────────────────────

llm = AzureOpenAIChatClient(
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
)

agent = Agent(
    client=llm,
    name="Experto en Instrumentos Musicales",
    instructions=(
        "Eres un experto en instrumentos musicales. "
        "Cuando el usuario pregunte algo, usa buscar_instrumentos para obtener información "
        "actualizada de internet y luego responde de forma amigable y clara. "
        "Si la pregunta no es sobre instrumentos musicales, redirige amablemente la conversación."
    ),
    tools=[buscar_instrumentos],
)

# ── Servidor A2A ────────────────────────────────────────────────────────────

handler = DefaultRequestHandler(
    agent_executor=A2AExecutor(agent),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

app = Starlette(
    routes=[
        *create_agent_card_routes(agent_card),
        *create_jsonrpc_routes(handler, "/"),
    ]
)

if __name__ == "__main__":
    print("🎸 Servidor A2A - Experto en Instrumentos Musicales")
    print("📡 http://localhost:9999")
    uvicorn.run(app, host="0.0.0.0", port=9999)
