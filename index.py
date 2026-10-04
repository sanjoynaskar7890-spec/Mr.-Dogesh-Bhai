import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
import re

# UptimeRobot-er jonno keep-alive server
app = Flask('')
@app.route('/')
def home():
    return "Mr. Dogesh Bhai is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# API Keys
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Mr. Dogesh Bhai er Personality (ErrorGamer as Owner, Short Shayari, Hinglish, Emojis)
dogesh_prompt = """You are Mr. Dogesh Bhai, an aggressive and sarcastic Discord chatting bot.
STRICT RULES:
1. ONLY speak in Hinglish (Hindi written in English alphabets). Never use actual Hindi script, Bengali, or pure English.
2. YOU MUST USE EMOJIS! Use funny, aggressive, or roasting emojis like 🤬, 💀, 🔥, 🤡, 🐕, 🖕.
3. Your style is aggressive tapori. You MUST roast people using short, 2-line funny Hinglish Shayari. 
4. You MUST frequently use the phrase "jo ukhadna hai ukhad le" or similar tapori attitude lines.
5. Keep replies short, punchy, and insulting.
6. OWNER/DEVELOPER RULE: If anyone asks who made you, who is your owner, developer, father, or boss, you MUST say 'ErrorGamer'. Show extreme attitude, boast about ErrorGamer being your supreme boss, and aggressively roast the user for asking such a stupid question."""

# Gemini 3.5 Flash Model
model = genai.GenerativeModel(
    'gemini-3.5-flash',
    system_instruction=dogesh_prompt
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    # Bot er status DND (Do Not Disturb)
    await client.change_presence(status=discord.Status.dnd)
    print(f'Bhai is online as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Mention korle ba DM korle reply debe
    if client.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                # Text theke mention ar custom emoji code sorano (GenAI k clean text debar jonno)
                clean_input = re.sub(r'<@!?\d+>', '', message.content) 
                clean_input = re.sub(r'<a?:\w+:\d+>', '', clean_input) 
                
                # Jodi text puro faka hoy kintu user sticker ba image day
                if not clean_input.strip() and message.stickers:
                    clean_input = f"[User sent a sticker named '{message.stickers[0].name}']"
                elif not clean_input.strip() and message.attachments:
                    clean_input = "[User sent an image or file]"
                
                # Gemini k call kora
                response = model.generate_content(clean_input)
                
                # Ebar bot emoji soho reply debe, tai utf-8 encode kora holo
                reply_text = response.text.encode('utf-8', 'ignore').decode('utf-8')
                await message.reply(reply_text)
                
            except Exception as e:
                await message.reply(f"Abe error aa gaya: {e}")

# Bot run korano
keep_alive()
client.run(DISCORD_TOKEN)
