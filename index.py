import discord
import os
import aiohttp
from flask import Flask
from threading import Thread
import re

app = Flask('')

@app.route('/')
def home():
    return "Mr. Dogesh Bhai zinda hai aur daud raha hai!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

dogesh_prompt = """Tu Mr. Dogesh Bhai hai, ekdum khatarnak, tapori aur sarcastic Discord bot.
STRICT RULES:
1. SIRF aur SIRF Hinglish (English alphabet mein Hindi) mein baat karni hai. Bengali ya pure English use mat karna.
2. EMOJIS use karna compulsory hai! 🤬, 💀, 🔥, 🤡, 🐕, 🖕 aise emojis daba ke use kar.
3. Tera style ekdum aggressive aur tapori hona chahiye. Logo ki beizzati chote 2-line Hinglish shayari se kar.
4. Beech beech mein "jo ukhadna hai ukhad le" ya uske jaisa tapori dialogue chipka diya kar.
5. Reply chhota, kadak aur pura beizzati wala hona chahiye.
6. OWNER/DEVELOPER RULE: Agar koi puche ki tujhe kisne banaya, tera malik, baap ya boss kaun hai, toh seedha bol 'ErrorGamer'. Full attitude dikha aur usko ghatiya sawal puchne ke liye pel de."""

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd)
    print(f'Bhai online aa gaya as {client.user}')

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
                        clean_input = f"[User ne ek sticker bheja hai jiska naam hai '{message.stickers[0].name}']"
                    elif message.attachments:
                        clean_input = "[User ne ek photo ya file bheji hai]"
                    else:
                        clean_input = "[User ne tujhe bina kuch bole ping/tag kiya hai. Apna time waste karne ke liye usko daba ke roast kar.]"
                
                final_input = dogesh_prompt + "\n\nUSER'S MESSAGE TO ROAST: " + clean_input
                
                # Direct gemini-1.5-flash select kora holo
                model_name = "models/gemini-1.5-flash"
                
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={GEMINI_API_KEY}"
                
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
                await message.reply(f"Abe code mein kuch gadbad hai, error aa gaya: {e}")

keep_alive()
client.run(DISCORD_TOKEN)
