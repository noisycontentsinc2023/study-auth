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
    # 랜덤하게 선택될 항목들
    choices = ['녹음하기', '단어 3개쓰기', '학습지 한 강 학습하고 인증하기', '학습하는 언어와 관련된 음식 먹기', '항목5', '항목6', '항목7', '항목8', '항목9', '항목10']

    # 결과가 출력될 임베드 메시지 생성
    embed = discord.Embed(title='추첨 결과', color=0xff0000)

    # 최종 결과 랜덤 선택을 위한 변수 설정
    result = ''

    # 0.5초 간격으로 랜덤한 항목들을 임베드 메시지에 추가
    for i in range(10):
        embed.set_footer(text='')
        embed.clear_fields()
        embed.add_field(name='추첨 중...', value=random.choice(choices), inline=False)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(0.5)

    # 5초 카운트 다운
    for i in range(5):
        embed.set_footer(text=f'{5-i}초 남았습니다')
        await message.edit(embed=embed)
        await asyncio.sleep(1)

    # 최종 결과 랜덤 선택
    result = random.choice(choices)
    embed.clear_fields()
    embed.add_field(name='추첨 결과', value=result, inline=False)
    embed.set_footer(text='오늘의 미션입니다!')
    await message.edit(embed=embed)
        
#Run the bot
bot.run(TOKEN)
