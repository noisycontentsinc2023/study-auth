import discord
import bs4
import asyncio
import os
import urllib
import requests
from discord import Embed
from discord.ext import tasks, commands
from discord.utils import get
from urllib.request import Request

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']

intents = discord.Intents.default()
intents.members = True
intents=discord.Intents.all()
prefix = '!'
bot = commands.Bot(command_prefix=prefix, intents=intents)

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.command(name='고정')
async def pin(ctx, message_id: int):
    try:
        channel = ctx.channel
        message = await channel.fetch_message(message_id)
        await message.pin()
        await ctx.send(f"Message {message_id} pinned to the bottom of the channel.")
    except discord.NotFound:
        await ctx.send("Message not found.")

@bot.command(name='해제')
async def unpin(ctx, message_id: int):
    try:
        channel = ctx.channel
        message = await channel.fetch_message(message_id)
        await message.unpin()
        await ctx.send(f"Message {message_id} unpinned.")
    except discord.NotFound:
        await ctx.send("Message not found.")
    
#Run the bot
bot.run(TOKEN)
