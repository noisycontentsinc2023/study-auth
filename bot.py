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
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_info = {
  "type": "service_account",
  "project_id": "thematic-bounty-382700",
  "private_key_id": "502d8dd4f035d15b57bff64ee323d544d28aedc4",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQD4Kze3Hn/yxevG\nzHUklYGSDDs8qKQeyYdd1eWaR0PNKZ2+nwKFGmXGENS6vuy3U81dqI3AVgA3w6UW\nHEaVfPvc31OX5yNCIS0eQxxqWWGJJ5+MbvUC06qXi/7hCup0WK+hoqwjHtUX7AYu\nEDgtf6xd29gSvb3YXs6pvi+2tpwPt0SED6HGPU7qPRsAaPnyUsVCj/mW04ca2iea\nxMsIqxKT6ufNssiXX7qhKyziowneM0lp8BB3k2z+/FGPQOCdi/lIscC9zKbDOIcb\nOZw+B2sd2opp7Dwo3JMIkh3NJevw9hjp0+CFeqemGNsCAiSuFkvydx6BagWaWAPs\nC48nZLNZAgMBAAECggEAF3uUbTMZQZZVoAU5CPYOMY0PfmcJR6IDeX8715BKg8N+\nOhtHBGQJ8Rbm4Ehgcxz+i/AfAK4KnXw5dvkEO1E9Lmph+Tfdg9yKjchlLBGK24z4\nqZPWwpaXl/k+7BnJs2pwbROs5PJeEOJMN+fgPvrrqyJ6RNS4Pf0Dond9AZWwOQLL\naJPFZryK7Bmvtt0H8mDDWdfqmCQTtPJ9PUyDEUeenlyhuek8wH3GHcghOSlsCDF1\nW/3YXM9Vr/arE4V6hTLwXofrUnTuXTfo+DcaOIXpHqIPS+nCyzWZ0kAJ7/uKjhnN\nF4kgv9aXDX9Y7S+3irXazRhowfu2rGuPRO/2+FCuMQKBgQD+JRDctOrKvpl9zDaw\nWT2a3qmYuFf90+b8EkKsWzVBM7neEJlw1ZWxUZzkdHXwkxcM7w93BjZeXJRnI7HZ\n5sHMrRw3p7Cwy0REqC3GSbYMCIZ/98y5Ot5sOXamUCOtYnic1NG2PBzr9h94Nt7d\nZu9D7cD/kaogm9Fl9t1VMD3REQKBgQD5+vvxY0nUkzrPEHfAOnPRqt3fM9ryzmk9\n8WyffmWqaDcvb9pl1F/+/51u00cvh2Q6etvL0J850AB0AKC9QdYzIaSj4LeRNzjA\ns+K6Po5+HAYezxC1cYzFh+slAfX3gX9pa11f3aOltj4h7IXvqBB0iH4rl/i2KQ/G\ntSDa62K9yQKBgAXXEDYiKisSijBr2u3efx3p8/fAdLUug2ZTfRi819Jxv9msg/ol\nzlTOzU4qpvMqTiNL8w0HJYSxl+9u0I1zUgzEBZv5zIOjiCQTwUmHNBm+sGiMZzXy\ndl4CTAmyWb+IPcFM2qzXYMrDUyHOEP0BeooTEpZM4J3zNrKjI57rhuAhAoGAKWDC\nE1K8BdPZCC1RpSAHy8zcrPWIaGiCQx6TPFNPwMU/XTrGi9R7j1oAVTfjsJpYnNV5\nTGNb99XWPV1dPfaH3i7TcczglcjuO/eKsAlqzLUWzkK4IVCKXKgC5D1O2Yk17d03\nt4aYb/Wak0LzaJgJIUD2oYCmSoDBe8K/jX0o+wECgYBnxk9HR/23hjWaxrSnXGDB\nHxLXg9Wz5w0N+gdC/FNxknFOft+nsCMKWMocOtGYhJU3OvkTYYqL1iDsKoMb74xG\nVwB1fuoNrNp+aJ/CzbtZVT1WLzXG41e9cu2TuOy+wpDlryfJAZ6KNVgDOmhh8TR2\nz7T0rt1QSfOZILpiwpR4jg==\n-----END PRIVATE KEY-----\n",
  "client_email": "noisycontents@thematic-bounty-382700.iam.gserviceaccount.com",
  "client_id": "107322055541690533468",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/noisycontents%40thematic-bounty-382700.iam.gserviceaccount.com"
}
creds = service_account.Credentials.from_service_account_info(info=creds_info, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open('테스트').worksheet('고정')

sticky_messages = {}
for row in rows:
    sticky_messages[int(row[0])] = row[1]
    
# 스프레드시트에서 초기 고정 메시지를 가져옵니다.
sticky_messages = {}

for row in sheet.get_all_values():
    if len(row) == 2 and row[0].isdigit():
        sticky_messages[int(row[0])] = row[1]

last_sticky_messages = {}


@bot.command(name='고정')
async def sticky(ctx, *, message):
    global sticky_messages
    channel_id = ctx.channel.id
    sticky_messages[channel_id] = message

    # 스프레드시트에 고정 메시지를 저장합니다.
    if str(channel_id) in sheet.col_values(1):
        row_num = int(sheet.col_values(1).index(str(channel_id))) + 1
        sheet.update_cell(row_num, 2, message)
    else:
        row_num = len(sheet.col_values(1)) + 1
        sheet.update_cell(row_num, 1, str(channel_id))
        sheet.update_cell(row_num, 2, message)

    await ctx.send(f'메시지가 고정됐습니다!')

@bot.command(name='해제')
async def unsticky(ctx):
    global sticky_messages
    channel_id = ctx.channel.id

    if channel_id in sticky_messages:
        del sticky_messages[channel_id]

        # 스프레드시트에서 고정 메시지를 삭제합니다.
        row_num = int(sheet.col_values(1).index(str(channel_id))) + 1
        sheet.delete_row(row_num)

        await ctx.send('고정이 해제됐어요!')
    else:
        await ctx.send('이 채널에는 고정된 메시지가 없어요')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    global sticky_messages
    global last_sticky_messages

    channel_id = message.channel.id

    if channel_id in sticky_messages:
        if channel_id in last_sticky_messages:
            old_message = last_sticky_messages[channel_id]
            try:
                await old_message.delete()
            except discord.NotFound:
                pass

        new_message = await message.channel.send(sticky_messages[message.channel.id])
        last_sticky_messages[message.channel.id] = new_message
        
#Run the bot
bot.run(TOKEN)
