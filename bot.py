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
intents.messages = True
intents=discord.Intents.all()
prefix = '!'
bot = commands.Bot(command_prefix=prefix, intents=intents)

stichy_message = None
sticky_channel = None

@bot.command(name='fixed')
async def sticky(ctx, *, message):
    global sticky_message
    global sticky_channel
    sticky_message = message
    sticky_channel = ctx.channel
    await ctx. send(f'Sticky message set in this channel!')

@bot.command(name='disable')
async def unsticky(ctx):
    global sticky_message
    global sticky_channel
    sticky_message = None
    sticky_channel = None
    await ctx. send('Sticky message removed.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    global sticky_message
    global sticky_channel
    if sticky_message and sticky_channel and message.channel == sticky_channel:
        await message.channel.send(sticky_message)
    
#Run the bot
bot.run(TOKEN)
