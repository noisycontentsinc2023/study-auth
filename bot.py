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
from nltk.corpus import wordnet as wn

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
    # Items to be randomly selected
    choices = ['학습하는 언어 한 마디 녹음하기', '일취월장에 인증하기', '!메모 기능을 활용해서 안외워지는 단어 입력해보기', '학습하는 언어 유튜브 검색해보기', '미션 패스권!', 'item6', 'item7', 'item8', 'item9', 'item10']

    # Create an embed message that will output the result
    embed = discord.Embed(title='오늘의 미션', color=0xff0000)

    # Send the initial message and store the message ID
    message = await ctx.send(embed=embed)
    message_id = message.id

    # Randomly select 10 items from choices
    selected_choices = random.sample(choices, 10)

    # Add randomly selected items to the embed message at 0.2 second intervals and clear existing fields
    for i, choice in enumerate(selected_choices):
        embed.clear_fields()
        embed.add_field(name=f'{i+1}번 미션', value=choice, inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(0.2)

    # Randomize the final result from selected_choices
    result = random.choice(selected_choices)
    embed.clear_fields()
    embed.add_field(name='Lottery Result', value=result, inline=False)
    embed.set_footer(text='오늘의 미션입니다!')

    # Update the embed message
    await message.edit(embed=embed)
    
#------------------------------------------------#
@bot.command(name='오늘의단어')
async def word(ctx, language):
    lang_codes = {'영어': 'eng', '스페인어': 'spa', '중국어': 'cmn-s'}
    lang = lang_codes.get(language.lower(), None)
    if lang is None:
        await ctx.send(f"Sorry, I don't have word lists for the language {language}.")
        return

    synsets = wn.all_synsets(lang=lang)
    words = random.sample(list(set(synset.lemma_names(lang=lang) for synset in synsets)), 5)
    embed = discord.Embed(title=f"Word of the day in {language.capitalize()}", color=discord.Color.blue())
    for word in words:
        synset = wn.synset(f"{word}.n.{lang}.01")
        definition = synset.definition()
        examples = ", ".join(synset.examples()[:3])
        pronunciation = f"/{synset.pronunciations()[0].pronunciation}/" if synset.pronunciations() else "Not available"
        embed.add_field(name=word, value=f"Definition: {definition}\nExamples: {examples}\nPronunciation: {pronunciation}", inline=False)
    await ctx.send(embed=embed)

        
#Run the bot
bot.run(TOKEN)
