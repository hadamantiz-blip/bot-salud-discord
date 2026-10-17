import os
import threading
from flask import Flask
import discord
import google.generativeai as genai

# --- SERVIDOR WEB FLASK PARA RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Hadamantiz activo"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- CONFIGURACIÓN DE DISCORD Y GEMINI ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Configuración limpia del modelo estándar
model = genai.GenerativeModel('gemini-1.5-flash')

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
                response = model.generate_content(prompt_final)
                texto_respuesta = response.text
                
                if len(texto_respuesta) > 2000:
                    for i in range(0, len(texto_respuesta), 1900):
                        await message.channel.send(texto_respuesta[i:i+1900])
                else:
                    await message.channel.send(texto_respuesta)

            except Exception as e:
                print(f"🚨 ERROR CRÍTICO DE GEMINI: {str(e)}")
                await message.channel.send(f"⚠️ Error técnico: {str(e)[:100]}")

# Iniciar servidor web Flask
threading.Thread(target=run_flask, daemon=True).start()

# Iniciar bot de Discord
client.run(DISCORD_TOKEN)
