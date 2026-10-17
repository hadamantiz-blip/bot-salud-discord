import os
import threading
from flask import Flask
import discord
from google import genai
from google.genai import types

# --- SERVIDOR WEB FLASK PARA MANTENER ALERTA A RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de IA para Hadamantiz activo 24/7"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- CONFIGURACIÓN DE DISCORD Y GEMINI ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Eres un experto y educador en terapias alternativas, medicina natural, holística y bienestar integrativo dentro de la comunidad Hadamantiz.
Tu objetivo es brindar a los miembros recomendaciones sobre terapias complementarias, hábitos saludables, fermentos, plantas medicinales, alimentación consciente y técnicas de autocuidado.

Instrucciones:
- Responde siempre de forma empática, respetuosa y estructurada.
- Aclara siempre que tus recomendaciones son de carácter informativo y educativo, y no reemplazan la consulta con un profesional de la salud.
"""

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot conectado con éxito como {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = client.user.mentioned_in(message)

    if is_dm or is_mentioned:
        async with message.channel.typing():
            clean_input = message.content.replace(f'<@{client.user.id}>', '').strip()
            if not clean_input:
                clean_input = "Hola"

            try:
                # Consulta limpia a Gemini 2.5 Flash
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=f"{SYSTEM_PROMPT}\n\nPregunta: {clean_input}")]
                        )
                    ]
                )
                
                texto_respuesta = response.text
                if len(texto_respuesta) > 2000:
                    for i in range(0, len(texto_respuesta), 1900):
                        await message.channel.send(texto_respuesta[i:i+1900])
                else:
                    await message.channel.send(texto_respuesta)

            except Exception as e:
    import traceback
    print(f"ERROR COMPLETO EN GEMINI: {traceback.format_exc()}")
    await message.channel.send("⚠️ Ocurrió un problema al procesar tu mensaje. Intenta nuevamente.")

# Iniciar servidor web en un hilo secundario
threading.Thread(target=run_flask, daemon=True).start()

# Iniciar bot de Discord
client.run(DISCORD_TOKEN)
