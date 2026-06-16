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

            # Obtener el stream (sin await aquí)
            stream = agent.run(pregunta, stream=True, session=session)

            # Animación de espera + recoger respuesta simultáneamente
            puntos = 0
            texto_final = ""

            async def recoger():
                nonlocal texto_final
                async for update in stream:
                    for content in update.contents:
                        if hasattr(content, "text") and content.text:
                            texto_final += content.text

            tarea = asyncio.create_task(recoger())

            while not tarea.done():
                simbolo = ". " * (puntos % 4 + 1)
                print(f"\rAgente: {simbolo}  ", end="", flush=True)
                puntos += 1
                await asyncio.sleep(0.5)

            await tarea  # asegura que termine bien

            print(f"\rAgente: {texto_final}\n")


if __name__ == "__main__":
    asyncio.run(chat())