import discord
import openai
from dotenv import load_dotenv
from discord.ext import commands
import os

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

openai.api_key = OPENAI_API_KEY

async def buscar_historico_canal(canal, limit=5):
    messages_list = []
    async for message in canal.history(limit=limit):
        role = "user" if message.author.id != bot.user.id else "system"
        content = message.content
        messages_list.append(f"{role}: {content}")

    messages_list.reverse()
    return messages_list

def ask_gpt(mensagens):
    prompt = "\n".join(mensagens)
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=300
    )

    resposta = response['choices'][0]['text'].replace("system:", "").strip()
    return resposta

@bot.event
async def on_ready():
    print(f"A {bot.user.name} ficou ligado!")

@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return

        async with message.channel.typing():
            # Verificar se a mensagem começa com '\'
            if message.content.startswith("\\"):
                mensagens = await buscar_historico_canal(message.channel)
                resposta = ask_gpt(mensagens)

                await message.reply(resposta)

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await bot.process_commands(message)

bot.run(DISCORD_BOT_TOKEN)
