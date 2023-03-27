import discord
import bs4
import asyncio
import os
import urllib
import requests
import openai
from discord import Embed
from discord.ext import tasks, commands
from discord.utils import get
from urllib.request import Request

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']
OPENAI = os.environ['OPENAI']

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)
openai.api_key = "OPENAI"

async def process_gpt_request(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].text.strip()

def is_topic_allowed(question):
    allowed_topics = ["language", "korean", "chinese", "japanese", "spanish", "german", "french"]
    return any(topic in question for topic in allowed_topics)

@bot.command(name='gpt')
async def gpt(ctx, *, question):
    question = question.strip().lower()

    if is_topic_allowed(question):
        response = await process_gpt_request(question)
        await ctx.send(response)
    else:
        await ctx.send("I can only answer language-related questions or questions related to Korean, Chinese, Japanese, Spanish, German, or French. Please try asking a question related to one of these topics.")
    
#Run the bot
bot.run(TOKEN)
