import discord
import bs4
import asyncio
import os
import urllib
import requests
import openai
from discord import Embed
from discord.ext import tasks, commands
from discord.utils import get
from urllib.request import Request

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']
OPENAI = os.environ['OPENAI']

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False


bot = commands.Bot(command_prefix='!', intents=intents)
openai.api_key = "OPENAI"
async def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].text.strip()
    tokens_used = response.choices[0].usage["total_tokens"]
    return message, tokens_used

@bot.command(name="gpt")
async def gpt(ctx, *, message):
    prompt = f"{ctx.author.name}: {message}"
    response, tokens_used = await generate_response(prompt)
    await ctx.send(f"Response: {response}\nTokens used: {tokens_used}")

#Run the bot
bot.run(TOKEN)
