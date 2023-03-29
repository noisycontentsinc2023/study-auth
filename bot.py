import discord
import bs4
import asyncio
import os
import urllib
import requests
import openai
import datetime
from discord import Embed
from discord.ext import tasks, commands
from discord.utils import get
from urllib.request import Request

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

todos = {}
completed_dates = {}
creation_times = {}

@bot.command(name='할일')
async def todo(ctx, *, options=None):
    if options is None:
        if ctx.author.id in todos:
            todo_list = "\n".join([f"[{'O' if checked else ' '}] {option}" for option, checked in todos[ctx.author.id]])
            creation_time = creation_times.get(ctx.author.id, None)
            if creation_time is not None:
                creation_time_str = creation_time.strftime("%Y-%m-%d %H:%M:%S")
                embed = discord.Embed(title=f"Your TODO list (created at {creation_time_str}):", description=todo_list, color=discord.Color.green())
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Your TODO list:", description=todo_list, color=discord.Color.green())
                await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have any TODO list.")
    else:
        options = options.split(",")
        todos[ctx.author.id] = [(option.strip(), False) for option in options]
        creation_times[ctx.author.id] = datetime.datetime.now()
        await ctx.send("TODO 리스트가 작성됐어요")

@bot.command(name='취소')
async def cancel(ctx):
    if ctx.author.id in todos:
        del todos[ctx.author.id]
        await ctx.send("TODO list canceled.")
    else:
        await ctx.send("You don't have any TODO list.")

@bot.command(name='체크')
async def check(ctx, option_num: int):
    if ctx.author.id in todos and 0 <= option_num < len(todos[ctx.author.id]):
        todos[ctx.author.id][option_num] = (todos[ctx.author.id][option_num][0], True)
        all_checked = all(checked for option, checked in todos[ctx.author.id])
        await ctx.send(f"Option {option_num} checked.")
        if all_checked:
            embed = discord.Embed(title="Congratulations!", description="All options are checked!", color=discord.Color.green())
            await ctx.send(embed=embed)
    else:
        await ctx.send("Invalid option number.")

@bot.command(name='체크해제')
async def uncheck(ctx, option_num: int):
    if ctx.author.id in todos and 0 <= option_num < len(todos[ctx.author.id]):
        todos[ctx.author.id][option_num] = (todos[ctx.author.id][option_num][0], False)
        await ctx.send(f"Option {option_num} unchecked.")
    else:
        await ctx.send("Invalid option number.")


#Run the bot
bot.run(TOKEN)
