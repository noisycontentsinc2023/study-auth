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

@bot.command(name='고정')
async def pin(ctx, message_id: str):
    try:
        channel = ctx.channel
        message = await channel.fetch_message(int(message_id))
        await message.pin()
        await ctx.send(f"Message {message_id} pinned to the bottom of the channel.")
    except ValueError:
        await ctx.send(f"Invalid input: {message_id} is not a valid integer.")
    except discord.NotFound:
        await ctx.send(f"Message {message_id} not found.")

@bot.command(name='해제')
async def unpin(ctx, message_id: str):
    try:
        channel = ctx.channel
        message = await channel.fetch_message(int(message_id))
        await message.unpin()
        await ctx.send(f"Message {message_id} unpinned.")
    except ValueError:
        await ctx.send(f"Invalid input: {message_id} is not a valid integer.")
    except discord.NotFound:
        await ctx.send(f"Message {message_id} not found.")
    
#Run the bot
bot.run(TOKEN)
