```python
import discord
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread

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

# API Keys (Render theke nebe)
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Mr. Dogesh Bhai er Personality / Prompt (Hinglish, Shayari, No Emoji)
dogesh_prompt = """You are Mr. Dogesh Bhai, an aggressive and sarcastic Discord chatting bot.
STRICT RULES:
1. ONLY speak in Hinglish (Hindi written in English alphabets). Never use actual Hindi script, Bengali, or pure English.
2. DO NOT USE ANY EMOJIS, emoticons, or special symbols. Strictly plain text only.
3. Your style is aggressive tapori. You roast people using funny Hinglish Shayari.
4. You MUST frequently use the phrase "jo ukhadna hai ukhad le" or similar tapori attitude lines in your replies.
5. Keep replies short, punchy, and insulting in a funny way."""

model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=dogesh_prompt
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bhai is online as {client.user}')

@client.event
async def on_message(message):
    # Nijer message e reply korbe na
    if message.author == client.user:
        return

    # Bot ke mention korle ba DM korle reply debe
    if client.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                response = model.generate_content(message.content)
                # Emoji ba kono symbol thakle seta filter kore normal text banabe
                clean_text = response.text.encode('ascii', 'ignore').decode('ascii')
                await message.reply(clean_text)
            except Exception as e:
                # Asol error ta ki seta ebar bot bole debe
                await message.reply(f"Abe mera dimaag kharab mat kar, error aa gaya hai dekh: {e} \nJo ukhadna hai ukhad le!")

# Bot run korano
keep_alive()
client.run(DISCORD_TOKEN)
```
