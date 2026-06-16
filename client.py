"""
A2A Client — Chat con el Experto en Instrumentos Musicales
Uso: python client.py
"""

import asyncio
import httpx
from a2a.client import A2ACardResolver
from agent_framework import AgentSession
from agent_framework.a2a import A2AAgent

SERVER_URL = "http://localhost:9999"


async def chat():
    # Descubrir el agente
    async with httpx.AsyncClient(timeout=30.0) as http:
        resolver = A2ACardResolver(httpx_client=http, base_url=SERVER_URL)
        agent_card = await resolver.get_agent_card()

    print(f"\n🎸 {agent_card.name}")
    print("─" * 40)
    print("Pregúntame sobre instrumentos musicales.")
    print("Escribe 'salir' para terminar.\n")

    # Sesión compartida → mantiene contexto de conversación
    session = AgentSession(service_session_id="chat-session-1")

    async with A2AAgent(name=agent_card.name, agent_card=agent_card, url=SERVER_URL) as agent:
        while True:
            try:
                pregunta = input("Tú: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 ¡Hasta luego!")
                break

            if not pregunta:
                continue
            if pregunta.lower() == "salir":
                print("👋 ¡Hasta luego!")
                break

            print("\nAgente: ", end="", flush=True)

            async with agent.run(pregunta, stream=True, session=session) as stream:
                async for update in stream:
                    for content in update.contents:
                        if content.text:
                            print(content.text, end="", flush=True)
                await stream.get_final_response()

            print("\n")


if __name__ == "__main__":
    asyncio.run(chat())
