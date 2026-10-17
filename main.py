import os
import threading
import requests
from flask import Flask
import discord

# --- SERVIDOR WEB FLASK PARA RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Hadamantiz activo"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- CONFIGURACIÓN ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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
                prompt_final = f"Eres un experto y educador en terapias alternativas, medicina natural, holística y bienestar integrativo dentro de la comunidad Hadamantiz. Responde de forma empática y estructurada a la siguiente consulta: {clean_input}"
                
                # Petición HTTP directa a la API de Gemini (Sin conflictos de librerías)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{
                        "parts": [{"text": prompt_final}]
                    }]
                }
                
                response = requests.post(url, headers=headers, json=data)
                resultado_json = response.json()
                
                texto_respuesta = resultado_json['candidates'][0]['content']['parts'][0]['text']
                
                if len(texto_respuesta) > 2000:
                    for i in range(0, len(texto_respuesta), 1900):
                        await message.channel.send(texto_respuesta[i:i+1900])
                else:
                    await message.channel.send(texto_respuesta)

            except Exception as e:
                print(f"🚨 ERROR: {str(e)}")
                await message.channel.send("⚠️ Ocurrió un problema al procesar tu mensaje. Intenta nuevamente.")

# Iniciar servidor web Flask
threading.Thread(target=run_flask, daemon=True).start()

# Iniciar bot de Discord
client.run(DISCORD_TOKEN)
