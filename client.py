"""
A2A Client — Se conecta al Search Agent y envía preguntas
Uso: python client.py "tu pregunta aquí"
"""

import asyncio
import sys
import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent

SERVER_URL = "http://localhost:9999"


async def ask(question: str):
    print(f"\n🔍 Pregunta: {question}\n")

    async with httpx.AsyncClient(timeout=60.0) as http_client:
        # 1. Descubrir el agente (Agent Card)
        resolver = A2ACardResolver(httpx_client=http_client, base_url=SERVER_URL)
        agent_card = await resolver.get_agent_card()
        print(f"✅ Agente encontrado: {agent_card.name} v{agent_card.version}")
        print(f"   Skills: {[s.name for s in (agent_card.skills or [])]}\n")

    # 2. Enviar mensaje con streaming
    async with A2AAgent(
        name=agent_card.name,
        agent_card=agent_card,
        url=SERVER_URL,
    ) as agent:
        print("💬 Respuesta:\n")
        async with agent.run(question, stream=True) as stream:
            async for update in stream:
                for content in update.contents:
                    if content.text:
                        print(content.text, end="", flush=True)

            final = await stream.get_final_response()
            print(f"\n\n✔ Completado ({len(final.messages)} mensaje(s))")


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "¿Qué novedades hay sobre Azure OpenAI en 2025?"
    asyncio.run(ask(question))
