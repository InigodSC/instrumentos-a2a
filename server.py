"""
A2A Server — Agente de búsqueda con SerpAPI + Azure OpenAI
Expone el agente en http://localhost:9999
"""

import os
import uvicorn
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

# ── Herramientas (tools) ────────────────────────────────────────────────────

def search_web(query: str) -> str:
    """Busca en internet usando SerpAPI y devuelve los resultados."""
    import httpx

    params = {
        "q": query,
        "api_key": os.environ["SERPAPI_KEY"],
        "num": 5,
    }
    response = httpx.get("https://serpapi.com/search", params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    results = []
    for r in data.get("organic_results", [])[:5]:
        title = r.get("title", "Sin título")
        snippet = r.get("snippet", "")
        link = r.get("link", "")
        results.append(f"- **{title}**\n  {snippet}\n  {link}")

    return "\n\n".join(results) if results else "No se encontraron resultados."


# ── AgentCard (tarjeta de presentación del agente) ──────────────────────────

search_skill = AgentSkill(
    id="web_search",
    name="Búsqueda Web",
    description="Busca información en internet usando SerpAPI.",
    tags=["search", "internet", "serpapi"],
    examples=["¿Qué es LangGraph?", "Últimas noticias sobre Azure OpenAI"],
)

agent_card = AgentCard(
    name="Search Agent",
    description="Agente especializado en búsqueda web con SerpAPI y Azure OpenAI.",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[
        AgentInterface(url="http://localhost:9999/", protocol_binding="JSONRPC"),
    ],
    skills=[search_skill],
)

# ── Agente ──────────────────────────────────────────────────────────────────

client = AzureOpenAIChatClient(
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
)

agent = Agent(
    client=client,
    name="Search Agent",
    instructions=(
        "Eres un asistente especializado en búsqueda web. "
        "Cuando el usuario haga una pregunta, usa la herramienta search_web "
        "para buscar información actualizada y luego responde de forma clara y concisa."
    ),
    tools=[search_web],
)

# ── Servidor A2A ────────────────────────────────────────────────────────────

request_handler = DefaultRequestHandler(
    agent_executor=A2AExecutor(agent),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

app = Starlette(
    routes=[
        *create_agent_card_routes(agent_card),
        *create_jsonrpc_routes(request_handler, "/"),
    ]
)

if __name__ == "__main__":
    print("🚀 Servidor A2A arrancando en http://localhost:9999")
    print("📋 Agent Card disponible en http://localhost:9999/.well-known/agent.json")
    uvicorn.run(app, host="0.0.0.0", port=9999)
