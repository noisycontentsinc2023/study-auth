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
@bot.command(name='미션')
async def lottery(ctx):
    # Items to be randomly selected
    choices = ['학습하는 언어 한 마디 녹음하기', '일취월장에 인증하기', '!메모 기능을 활용해서 안외워지는 단어 입력해보기', '학습하는 언어 유튜브 검색해보기', 'item5', 'item6', 'item7', 'item8', 'item9', 'item10']

    # Create an embed message that will output the result
    embed = discord.Embed(title='Lottery result', color=0xff0000)

    # Send the initial message and store the message ID
    message = await ctx.send(embed=embed)
    message_id = message.id

    # Add random items to the embed message at 0.5 second intervals
    for i in range(10):
        embed.clear_fields() # clear fields before adding new item
        embed.add_field(name=f'{i+1}th item', value=random.choice(choices), inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)

    # 5 seconds countdown
    for i in range(5):
        embed.set_footer(text=f'{5-i} seconds left')
        await message.edit(embed=embed)
        await asyncio.sleep(1)

    # Randomize the final result
    result = random.choice(choices)
    embed.add_field(name='Lottery Result', value=result, inline=False)
    embed.set_footer(text='Congratulations!')

    # Update the embed message
    await message.edit(embed=embed)
        
#Run the bot
bot.run(TOKEN)
