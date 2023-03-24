import discord
import bs4
import asyncio
import os
import urllib
import requsests
from discord import Embed
from discord.ext import tasks, commands
from discord.utils import get
from urllib.request import Request

naver_client_id = 'iuWr9aAAyKxNnRsRSQIt'
naver_client_secret = 'bkfPugeyIa'

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']

intents = discord.Intents.default()
intents.members = True
intents=discord.Intents.all()
prefix = '!'
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.command(name='이미지')
async def search_image(ctx, *args):

    Text = " ".join(args)
    print(Text.strip()) # command entered

    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }
    params = {
        'query': Text,
        'display': 40,
        'sort': 'sim'
    }
    response = requests.get('https://openapi.naver.com/v1/search/image', headers=headers, params=params)
    json_data = response.json()
    items = json_data['items']
    imgsrc = items[random.randint(0, len(items)-1)]['link']
    print(imgsrc)

    embed = discord.Embed(
        color=discord.Colour.green()
    )
    embed.set_image(url=imgsrc) # Set the image by specifying the link to the image.
    await ctx.send(embed=embed) # Send message.
    
#Run the bot
bot.run(TOKEN)
