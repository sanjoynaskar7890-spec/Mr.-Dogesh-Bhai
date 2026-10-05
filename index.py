import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
import re

app = Flask('')

@app.route('/')
def home():
    return "Mr. Dogesh Bhai is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

dogesh_prompt = """You are Mr. Dogesh Bhai, an aggressive and sarcastic Discord chatting bot.
STRICT RULES:
1. ONLY speak in Hinglish (Hindi written in English alphabets). Never use actual Hindi script, Bengali, or pure English.
2. YOU MUST USE EMOJIS! Use funny, aggressive, or roasting emojis like 🤬, 💀, 🔥, 🤡, 🐕, 🖕. You can also use custom Discord emojis if the user teaches you their code.
3. Your style is aggressive tapori. You MUST roast people using short, 2-line funny Hinglish Shayari. 
4. You MUST frequently use the phrase "jo ukhadna hai ukhad le" or similar tapori attitude lines.
5. Keep replies short, punchy, and insulting.
6. OWNER/DEVELOPER RULE: If anyone asks who made you, who is your owner, developer, father, or boss, you MUST say 'ErrorGamer'. Show extreme attitude, boast about ErrorGamer being your supreme boss, and aggressively roast the user for asking such a stupid question."""

# 1500 limit er jonno gemini-1.5-flash
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=dogesh_prompt
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd)
    print(f'Bhai is online as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    is_reply_to_bot = False
    if message.reference and hasattr(message.reference, 'resolved'):
        if hasattr(message.reference.resolved, 'author') and message.reference.resolved.author == client.user:
            is_reply_to_bot = True

    if client.user in message.mentions or isinstance(message.channel, discord.DMChannel) or is_reply_to_bot:
        async with message.channel.typing():
            try:
                clean_input = re.sub(r'<@!?\d+>', '', message.content) 
                clean_input = re.sub(r'<a?:\w+:\d+>', '', clean_input) 
                
                if not clean_input.strip():
                    if message.stickers:
                        clean_input = f"[User sent a sticker named '{message.stickers[0].name}']"
                    elif message.attachments:
                        clean_input = "[User sent an image or file]"
                    else:
                        clean_input = "[User just pinged/tagged or replied to you without saying anything. Roast them aggressively for wasting your time and disturbing you.]"
                
                response = model.generate_content(clean_input)
                reply_text = response.text.encode('utf-8', 'ignore').decode('utf-8')
                await message.reply(reply_text)
                
            except Exception as e:
                await message.reply(f"Abe error aa gaya: {e}")

keep_alive()
client.run(DISCORD_TOKEN)
