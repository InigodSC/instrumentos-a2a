# A2A Search Agent

Comunicación cliente-servidor con el protocolo A2A.  
El **servidor** expone un agente de búsqueda web (SerpAPI + Azure OpenAI).  
El **cliente** lo descubre y le envía preguntas.

## Estructura

```
a2a_search_agent/
├── server.py        ← Agente A2A (SerpAPI + Azure OpenAI)
├── client.py        ← Cliente A2A
├── .env.example     ← Credenciales (copia a .env y rellena)
└── requirements.txt
```

## Setup

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar credenciales
cp .env.example .env
# → Edita .env con tus claves reales
```

## Uso

**Terminal 1 — arrancar el servidor:**
```bash
python server.py
```

**Terminal 2 — enviar una pregunta:**
```bash
python client.py "¿Cuáles son las últimas novedades de Azure OpenAI?"
```

## Cómo funciona

```
Cliente                          Servidor (puerto 9999)
  │                                      │
  ├─ GET /.well-known/agent.json ────────► AgentCard (nombre, skills...)
  │◄──────────────────────────────────────┤
  │                                      │
  ├─ POST / (mensaje usuario) ───────────► AzureOpenAI decide usar search_web()
  │                                      │ → SerpAPI busca en internet
  │◄── stream de respuesta ───────────────┤ → LLM sintetiza y responde
```

## Credenciales necesarias

| Variable | Dónde obtenerla |
|---|---|
| `AZURE_OPENAI_ENDPOINT` | Azure Portal → tu recurso OpenAI |
| `AZURE_OPENAI_DEPLOYMENT` | Nombre del deployment (ej: `gpt-4o-mini`) |
| `AZURE_OPENAI_API_KEY` | Azure Portal → Keys |
| `SERPAPI_KEY` | https://serpapi.com → Dashboard |
