import discord
import bs4
import asyncio
import os
import urllib
import requests
import openai
import datetime
import random
import json
import json.decoder
import gspread

from google.oauth2 import service_account
from discord import Embed
from discord.ext import tasks, commands
from discord.utils import get
from urllib.request import Request
from discord.ui import Select, Button, View

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']
OPENAI = os.environ['OPENAI']

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.typing = False
intents.presences = False


bot = commands.Bot(command_prefix=PREFIX, intents=intents)
openai.api_key = OPENAI

async def generate_response(prompt):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.8,
    )

    message = response.choices[0].text.strip()
    return message

@bot.command(name="gpt")
async def gpt(ctx, *, message):
    prompt = f"{ctx.author.name}: {message}"
    response = await generate_response(prompt)

    embed = discord.Embed(title="답변", description=response, color=discord.Color.blue())
    await ctx.send(embed=embed)
    
#------------------------------------------------#
@bot.command(name='추첨')
async def slot_machine(ctx):
    items = ['사과', '배', '딸기', '바나나', '귤', '포도', '수박', '참외', '메론', '복숭아']
    messages = []
    for i in range(10):
        item = random.choice(items)
        messages.append(await ctx.send(f'{i+1}. {item}'))
        
    for _ in range(5):
        for i in range(10):
            item = random.choice(items)
            await messages[i].edit(content=f'{i+1}. {item}')
            await asyncio.sleep(0.5)
            if i > 0:
                await messages[i-1].delete()
        await messages[-1].delete()

    result = random.choice(items)
    await ctx.send(f'추첨 결과: {result}')
        
#Run the bot
bot.run(TOKEN)
