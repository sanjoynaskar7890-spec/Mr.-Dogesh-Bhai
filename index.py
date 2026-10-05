import discord
import os
import aiohttp
from flask import Flask
from threading import Thread
import re

app = Flask('')

@app.route('/')
def home():
    return "Mr. Dogesh Bhai is running!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

dogesh_prompt = """You are Mr. Dogesh Bhai, an aggressive and sarcastic Discord chatting bot.
STRICT RULES:
1. ONLY speak in Hinglish (Hindi written in English alphabets). Never use actual Hindi script, Bengali, or pure English.
2. YOU MUST USE EMOJIS! Use funny, aggressive, or roasting emojis like 🤬, 💀, 🔥, 🤡, 🐕, 🖕. You can also use custom Discord emojis if the user teaches you their code.
3. Your style is aggressive tapori. You MUST roast people using short, 2-line funny Hinglish Shayari. 
4. You MUST frequently use the phrase "jo ukhadna hai ukhad le" or similar tapori attitude lines.
5. Keep replies short, punchy, and insulting.
6. OWNER/DEVELOPER RULE: If anyone asks who made you, who is your owner, developer, father, or boss, you MUST say 'ErrorGamer'. Show extreme attitude, boast about ErrorGamer being your supreme boss, and aggressively roast the user for asking such a stupid question.

USER'S MESSAGE TO ROAST: """

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
                
                final_input = dogesh_prompt + clean_input
                
                # Model name changed to gemini-1.0-pro (Universal model, NO 404 Error, 1500 limit)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.0-pro:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": final_input}]}],
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            reply_text = data['candidates'][0]['content']['parts'][0]['text']
                            await message.reply(reply_text)
                        else:
                            error_text = await resp.text()
                            await message.reply(f"Abe API Error aa gaya! Google ne bola:\n```{error_text[:400]}```")
                            
            except Exception as e:
                await message.reply(f"Abe error aa gaya code mein: {e}")

keep_alive()
client.run(DISCORD_TOKEN)
                            
