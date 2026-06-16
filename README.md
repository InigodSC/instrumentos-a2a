# 🎸 A2A Search Agent — Experto en Instrumentos Musicales

Chat cliente-servidor con el protocolo A2A.  
El **servidor** expone un agente experto en instrumentos musicales (SerpAPI + Azure OpenAI).  
El **cliente** es un chat interactivo que mantiene el contexto de la conversación.

## Estructura

```
a2a_search_agent/
├── server.py        ← Agente A2A (SerpAPI + Azure OpenAI)
├── client.py        ← Chat interactivo
├── .env.example     ← Credenciales (copia a .env y rellena)
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # rellena con tus claves
```

## Uso

**Terminal 1 — servidor:**
```bash
python server.py
```

**Terminal 2 — chat:**
```bash
python client.py
```

```
🎸 Experto en Instrumentos Musicales
────────────────────────────────────
Tú: ¿Diferencias entre guitarra clásica y flamenca?
Agente: La flamenca es más ligera, con tapa de abeto...

Tú: ¿Y cuánto cuesta una buena?
Agente: (recuerda el contexto anterior)...

Tú: salir
👋 ¡Hasta luego!
```

## Cómo funciona

```
Cliente                             Servidor :9999
  │                                      │
  ├─ GET /.well-known/agent.json ───────►│  Descubre el agente (AgentCard)
  │◄─────────────────────────────────────┤
  │                                      │
  ├─ "¿Qué es un sitar?" ───────────────►│  Azure OpenAI decide buscar
  │                                      │  → SerpAPI: "instrumento musical sitar"
  │◄── respuesta en streaming ───────────┤  → LLM sintetiza y responde
  │                                      │
  ├─ "¿Y de dónde viene?" ─────────────►│  Recuerda el contexto anterior
  │◄── respuesta en streaming ───────────┤
```

## Credenciales necesarias

| Variable | Dónde obtenerla |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | Azure Portal → tu recurso OpenAI |
| `AZURE_OPENAI_DEPLOYMENT` | Nombre del deployment (ej: `gpt-4o-mini`) |
| `AZURE_OPENAI_API_KEY` | Azure Portal → Keys |
| `SERPAPI_KEY` | https://serpapi.com → Dashboard |
