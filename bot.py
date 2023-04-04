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

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_info = {
  "type": "service_account",
  "project_id": "thematic-bounty-382700",
  "private_key_id": "502d8dd4f035d15b57bff64ee323d544d28aedc4",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQD4Kze3Hn/yxevG\nzHUklYGSDDs8qKQeyYdd1eWaR0PNKZ2+nwKFGmXGENS6vuy3U81dqI3AVgA3w6UW\nHEaVfPvc31OX5yNCIS0eQxxqWWGJJ5+MbvUC06qXi/7hCup0WK+hoqwjHtUX7AYu\nEDgtf6xd29gSvb3YXs6pvi+2tpwPt0SED6HGPU7qPRsAaPnyUsVCj/mW04ca2iea\nxMsIqxKT6ufNssiXX7qhKyziowneM0lp8BB3k2z+/FGPQOCdi/lIscC9zKbDOIcb\nOZw+B2sd2opp7Dwo3JMIkh3NJevw9hjp0+CFeqemGNsCAiSuFkvydx6BagWaWAPs\nC48nZLNZAgMBAAECggEAF3uUbTMZQZZVoAU5CPYOMY0PfmcJR6IDeX8715BKg8N+\nOhtHBGQJ8Rbm4Ehgcxz+i/AfAK4KnXw5dvkEO1E9Lmph+Tfdg9yKjchlLBGK24z4\nqZPWwpaXl/k+7BnJs2pwbROs5PJeEOJMN+fgPvrrqyJ6RNS4Pf0Dond9AZWwOQLL\naJPFZryK7Bmvtt0H8mDDWdfqmCQTtPJ9PUyDEUeenlyhuek8wH3GHcghOSlsCDF1\nW/3YXM9Vr/arE4V6hTLwXofrUnTuXTfo+DcaOIXpHqIPS+nCyzWZ0kAJ7/uKjhnN\nF4kgv9aXDX9Y7S+3irXazRhowfu2rGuPRO/2+FCuMQKBgQD+JRDctOrKvpl9zDaw\nWT2a3qmYuFf90+b8EkKsWzVBM7neEJlw1ZWxUZzkdHXwkxcM7w93BjZeXJRnI7HZ\n5sHMrRw3p7Cwy0REqC3GSbYMCIZ/98y5Ot5sOXamUCOtYnic1NG2PBzr9h94Nt7d\nZu9D7cD/kaogm9Fl9t1VMD3REQKBgQD5+vvxY0nUkzrPEHfAOnPRqt3fM9ryzmk9\n8WyffmWqaDcvb9pl1F/+/51u00cvh2Q6etvL0J850AB0AKC9QdYzIaSj4LeRNzjA\ns+K6Po5+HAYezxC1cYzFh+slAfX3gX9pa11f3aOltj4h7IXvqBB0iH4rl/i2KQ/G\ntSDa62K9yQKBgAXXEDYiKisSijBr2u3efx3p8/fAdLUug2ZTfRi819Jxv9msg/ol\nzlTOzU4qpvMqTiNL8w0HJYSxl+9u0I1zUgzEBZv5zIOjiCQTwUmHNBm+sGiMZzXy\ndl4CTAmyWb+IPcFM2qzXYMrDUyHOEP0BeooTEpZM4J3zNrKjI57rhuAhAoGAKWDC\nE1K8BdPZCC1RpSAHy8zcrPWIaGiCQx6TPFNPwMU/XTrGi9R7j1oAVTfjsJpYnNV5\nTGNb99XWPV1dPfaH3i7TcczglcjuO/eKsAlqzLUWzkK4IVCKXKgC5D1O2Yk17d03\nt4aYb/Wak0LzaJgJIUD2oYCmSoDBe8K/jX0o+wECgYBnxk9HR/23hjWaxrSnXGDB\nHxLXg9Wz5w0N+gdC/FNxknFOft+nsCMKWMocOtGYhJU3OvkTYYqL1iDsKoMb74xG\nVwB1fuoNrNp+aJ/CzbtZVT1WLzXG41e9cu2TuOy+wpDlryfJAZ6KNVgDOmhh8TR2\nz7T0rt1QSfOZILpiwpR4jg==\n-----END PRIVATE KEY-----\n",
  "client_email": "noisycontents@thematic-bounty-382700.iam.gserviceaccount.com",
  "client_id": "107322055541690533468",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/noisycontents%40thematic-bounty-382700.iam.gserviceaccount.com"
}
creds = service_account.Credentials.from_service_account_info(info=creds_info, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open('테스트').worksheet('메모')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.command(name='메모')
async def memo(ctx):
    # Extract user ID and memo content
    user_id = str(ctx.author.id)
    message_content = ctx.message.content
    memo = message_content.split('!메모 ')[1]

    # Find the next available column to write data to
    header_values = sheet.row_values(1)
    if not header_values:
        col = 1
        sheet.update_cell(1, col, user_id)
    elif user_id not in header_values:
        last_user_col = sheet.col_count
        last_user_id = header_values[-1]
        last_user_id_col = header_values.index(last_user_id) + 1
        col = last_user_id_col + 1
        sheet.add_cols(1)
        sheet.update_cell(1, col, user_id)
    else:
        col = header_values.index(user_id) + 1

    # Find the next available row to write data to
    values = sheet.col_values(col)
    row = len(values) + 1

    # Write user ID and memo content to the corresponding cell
    if row == 1:
        sheet.update_cell(row, col, user_id)
        row += 1
    sheet.update_cell(row, col, memo)

    await ctx.send(f'{ctx.author.mention} memo saved.')
    
@bot.command(name='메모보기')
async def view_memo(ctx):
    # Extract user ID
    user_id = str(ctx.author.id)

    # Find the column index of the user ID in row 1
    header_values = sheet.row_values(1)
    try:
        col = header_values.index(user_id) + 1
    except ValueError:
        await ctx.send(f'{ctx.author.mention} memo not found.')
        return

    # Retrieve memo content for the user from row 2
    memo_values = sheet.col_values(col)[1:]
    if memo_values:
        memo_list = [f'{i+1}. {memo}' for i, memo in enumerate(memo_values)]
        memo_str = '\n'.join(memo_list)
        embed = discord.Embed(title=f'Memo for {ctx.author.name}', description=memo_str)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'{ctx.author.mention} memo not found.')
        
@bot.command(name='메모삭제')
async def delete_memo(ctx, memo_number: int):
    # Extract user ID and memo content
    user_id = str(ctx.author.id)
    message_content = ctx.message.content
    memo = message_content.split('!메모삭제 ')[1]

    # Define the column letter
    col_letter = 'A'

    # Find the column index of the user ID in row 1
    header_values = sheet.row_values(1)
    try:
        col = header_values.index(user_id) + 1
    except ValueError:
        await ctx.send(f'{ctx.author.mention} memo not found.')
        return

    # Retrieve memo content for the user from row 2
    memo_range = sheet.get(f'{col_letter}{row_start}:{col_letter}{sheet.row_count}')
    memo_values = memo_range[1:]
    memo_contents = [row[0].value for row in memo_values]

    # Check if the given memo number is valid
    if memo_number <= 0 or memo_number > len(memo_contents):
        await ctx.send(f'{ctx.author.mention} invalid memo number.')
        return

    # Find the index of the memo content to delete
    index_to_delete = memo_contents.index(f'{memo_number}. {user_id}: {memo}') + 2

    # Delete the memo content from the spreadsheet
    sheet.update_cell(index_to_delete, col, '')

    # Shift remaining memo numbers up by one
    memo_range = sheet.get(f'{col_letter}{row_start}:{col_letter}{sheet.row_count}')
    memo_values = memo_range[1:]
    for i, row in enumerate(memo_values):
        memo_number = i + 1
        row[0].update_value(f'{memo_number}. {user_id}: {row[0].value}')
    sheet.update(f'{col_letter}{row_start}:{col_letter}{sheet.row_count}', memo_values)

    await ctx.send(f'{ctx.author.mention} memo {memo_number} deleted.')
        
#-------------------------사다리임-------------------------#
        
@bot.command(name='운세')
async def Fortune(ctx):
    embed = discord.Embed(title="2023년 외국어 운세보기", description="올해 나의 운세를 외국어로 점쳐봅시다!", color=0xffd700)
    embed.set_footer(text="클릭하여 운세를 확인하세요!")
    button = discord.ui.Button(style=discord.ButtonStyle.primary, label="올해 나의 운세는?", url="https://bit.ly/2023_fortune")
    view = discord.ui.View()
    view.add_item(button)
    await ctx.send(embed=embed, view=view)

@bot.command(name='공부')
async def study(ctx):
    if random.random() < 0.8:
        message = "오늘 같은 날은 집에서 공부하고 일취월장 인증 어떠신가요🥳"
    else:
        message = "오늘 공부는 패스!"
    embed = discord.Embed(title="Study message", description=message, color=0xffd700)
    await ctx.send(embed=embed)
    
#Run the bot
bot.run(TOKEN)
