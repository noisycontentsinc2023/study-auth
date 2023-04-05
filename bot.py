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
class SlotMachineButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='START', style=discord.ButtonStyle.blurple)
        self.disabled = False
        
    async def on_button_click(self, button, interaction):
        if self.label == 'STOP':
            return
        
        self.disabled = True
        self.label = 'STOP'
        await interaction.response.edit_message(content='추첨을 시작합니다!')
        results = ['꽝', '꽝', '꽝', '꽝', '당첨!']
        for i in range(5):
            result_message = ' '.join(random.sample(results, len(results)))
            await interaction.message.edit(content=f'[{i+1}번째] {result_message}')
            await interaction.response.defer(edit_origin=True)
            await asyncio.sleep(1.0)

        result = random.choice(results)
        await interaction.message.edit(content=f'추첨 결과: {result}')
        self.disabled = False
        self.label = 'START'

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='추첨')
async def slot_machine(ctx):
    view = discord.ui.View()
    view.add_item(SlotMachineButton())
    await ctx.send('버튼을 눌러서 추첨을 시작하세요!', view=view)
        
#Run the bot
bot.run(TOKEN)
