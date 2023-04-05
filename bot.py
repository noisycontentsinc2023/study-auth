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

@bot.command(name='가위')
async def rock_paper_scissors(ctx):
    user_choice = '가위'
    await play_game(user_choice, ctx)

@bot.command(name='바위')
async def rock_paper_scissors(ctx):
    user_choice = '바위'
    await play_game(user_choice, ctx)

@bot.command(name='보')
async def rock_paper_scissors(ctx):
    user_choice = '보'
    await play_game(user_choice, ctx)

async def play_game(user_choice, ctx):
    rps = ['가위', '바위', '보']
    bot_choice = random.choice(rps)

    result = None
    if user_choice == bot_choice:
        result = '비겼습니다!'
        color = discord.Color.dark_gray()
        emoji = '🤝'
    elif (user_choice == '가위' and bot_choice == '보') or \
         (user_choice == '바위' and bot_choice == '가위') or \
         (user_choice == '보' and bot_choice == '바위'):
        result = '테이망령이 졌습니다!😭'
        color = discord.Color.green()
        emoji = '🎉'
    else:
        result = '테이망령이 이겼습니다!🥳'
        color = discord.Color.red()
        emoji = '😭'

    embed = discord.Embed(title=f'{user_choice} 대 {bot_choice}', description=result, color=color)
    embed.set_author(name='게임 결과')

    await ctx.send(embed=embed)
    
#Run the bot
bot.run(TOKEN)
