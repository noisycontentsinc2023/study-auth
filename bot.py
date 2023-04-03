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
import discord_components
from discord_components import DiscordComponents, Button
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

async def reset_todos():
    while True:
        now = datetime.datetime.now()
        reset_time = datetime.datetime.combine(now.date(), datetime.time(hour=0))
        if now >= reset_time:
            # Reset TODO lists for each user
            todos.clear()
            completed_dates.clear()
            creation_times.clear()
        await asyncio.sleep(3600)  # Check every hour

@bot.event
async def on_ready():
    print("Bot is ready.")
    bot.loop.create_task(reset_todos())

@bot.command(name='할일')
async def todo(ctx, *, options=None):
    if ctx.author.id in todos and all(checked for _, checked in todos[ctx.author.id]):
        await ctx.send("오늘의 TODO list 를 모두 완료했습니다!")
    elif options is None:
        if ctx.author.id in todos:
            todo_list = "\n".join([f"[{'O' if checked else ' '}] {option}" for option, checked in todos[ctx.author.id]])
            creation_time = creation_times.get(ctx.author.id, None)
            if creation_time is not None:
                creation_time_str = creation_time.strftime("%Y-%m-%d %H:%M:%S")
                embed = discord.Embed(title=f"TODO list (만들어진 시간 {creation_time_str}):", description=todo_list, color=discord.Color.green())
                await ctx.send(f"{ctx.author.mention}", embed=embed)
            else:
                embed = discord.Embed(title="TODO list:", description=todo_list, color=discord.Color.green())
                await ctx.send(f"{ctx.author.mention}", embed=embed)
        elif options == "complete":
            if all(checked for _, checked in todos.get(ctx.author.id, [])):
                embed = discord.Embed(title="Congratulations!", description="All options are checked!", color=discord.Color.green())
                await ctx.send(embed=embed)
            else:
                await ctx.send("Not all options are checked.")
        else:
            await ctx.send("현재 TODO list 가 작성되지 않았어요")
    else:
        options = options.split(",")
        todos[ctx.author.id] = [(option.strip(), False) for option in options]
        creation_times[ctx.author.id] = datetime.datetime.now()
        await ctx.send("TODO list 가 작성되었습니다!")
        
@bot.command(name='취소')
async def cancel(ctx):
    if ctx.author.id in todos:
        del todos[ctx.author.id]
        await ctx.send("TODO list 가 취소됐어요")
    else:
        await ctx.send("작성된 TODO list 가 없습니다")

@bot.command(name='체크')
async def check(ctx, option_num: int):
    if ctx.author.id in todos and 0 <= option_num < len(todos[ctx.author.id]):
        todos[ctx.author.id][option_num] = (todos[ctx.author.id][option_num][0], True)
        all_checked = all(checked for option, checked in todos[ctx.author.id])
        await ctx.send(f"{option_num}번 째 TODO list 가 체크 됐어요!")
        if all_checked:
            embed = discord.Embed(title="축하드립니다!", description="모든 TODO list 가 완료됐어요!", color=discord.Color.green())
            await ctx.send(embed=embed)
    else:
        await ctx.send("TODO list에 없는 항목이에요")

@bot.command(name='체크해제')
async def uncheck(ctx, option_num: int):
    if ctx.author.id in todos and 0 <= option_num < len(todos[ctx.author.id]):
        todos[ctx.author.id][option_num] = (todos[ctx.author.id][option_num][0], False)
        await ctx.send(f"Option {option_num} unchecked.")
    else:
        await ctx.send("TODO list 에 없는 항목이에요")
        
#-------------------------메-------------------------#

memo_dict = {}

def load_memo():
    global memo_dict
    try:
        with open('memo.json', 'r') as f:
            memo_dict = json.load(f)
            print("Loaded memo from memo.json")
    except FileNotFoundError:
        print("memo.json not found, creating a new file.")
        memo_dict = {}
        save_memo()
    except json.decoder.JSONDecodeError:
        print("memo.json contains invalid JSON data, creating a new file.")
        memo_dict = {}
        save_memo()

def save_memo():
    try:
        with open('memo.json', 'w') as f:
            json.dump(memo_dict, f)
        print("Saved memo to memo.json")
    except Exception as e:
        print(f"Error while saving memo.json: {e}")

@bot.event
async def on_ready():
    print("Bot is ready.")
    print(f"Current working directory: {os.getcwd()}")
    load_memo()

@bot.command(name='메모')
async def add_memo(ctx, memo_topic: str, *, memo_content: str):
    memo_topic = memo_topic.strip()
    memo_content = memo_content.strip()
    if memo_topic in memo_dict:
        memo_dict[memo_topic].append(memo_content)
    else:
        memo_dict[memo_topic] = [memo_content]
    save_memo()
    await ctx.send(f"Memo '{memo_topic}' added.")

@bot.command(name='메모보기')
async def show_memo(ctx):
    author_mention = ctx.message.author.mention
    load_memo()
    for memo_topic, memo_contents in memo_dict.items():
        embed = discord.Embed(title=memo_topic)
        for i, memo_content in enumerate(memo_contents):
            embed.add_field(name=f"Content {i+1}", value=memo_content, inline=False)
        await ctx.send(embed=embed)
        
#-------------------------사다리임-------------------------#
        
@bot.command(name='운세')
async def Fortune(ctx):
    embed = discord.Embed(title="Fortune for 2023", description="What is your fortune for this year in 2023?", color=0xffd700)
    embed.set_footer(text="Click here for your fortune!")
    button = discord.ui.Button(label="Your Fortune", url="https://bit.ly/2023_fortune")
    action_row = discord.ui.ActionRow(button)
    await ctx.send(embed=embed, components=[action_row])
    
#Run the bot
bot.run(TOKEN)
