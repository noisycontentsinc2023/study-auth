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

@bot.command(name='고정')
async def sticky(ctx, *, message):
    global sticky_messages
    sticky_messages[ctx.channel.id] = message
    await ctx.send(f'Sticky message set in this channel!')

@bot.command(name='해제')
async def unsticky(ctx):
    global sticky_messages
    if ctx.channel.id in sticky_messages:
        del sticky_messages[ctx.channel.id]
        await ctx.send('Sticky message removed.')
    else:
        await ctx.send('No sticky message found in this channel.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    global sticky_messages
    if message.channel.id in sticky_messages:
        await message.channel.send(sticky_messages[message.channel.id])
    
#Run the bot
bot.run(TOKEN)
