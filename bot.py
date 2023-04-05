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

    await ctx.send(f'{ctx.author.mention} 메모가 저장됐어요')
    
@bot.command(name='메모보기')
async def view_memo(ctx):
    # Extract user ID
    user_id = str(ctx.author.id)

    # Find the column index of the user ID in row 1
    header_values = sheet.row_values(1)
    try:
        col = header_values.index(user_id) + 1
    except ValueError:
        await ctx.send(f'{ctx.author.mention} 메모를 찾을 수 없습니다 :(')
        return

    # Retrieve memo content for the user from row 2
    memo_values = sheet.col_values(col)[1:]
    if memo_values:
        memo_list = [f'{i+1}. {memo}' for i, memo in enumerate(memo_values)]
        memo_str = '\n'.join(memo_list)
        embed = discord.Embed(title=f"{ctx.author.name}의 메모입니다", description=memo_str)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'{ctx.author.mention} 메모를 찾지 못했어요')
        
@bot.command(name='메모삭제')
async def delete_memo(ctx, memo_numbers: str):
    # Extract user ID
    user_id = str(ctx.author.id)

    # Find the column index of the user ID in row 1
    header_values = sheet.row_values(1)
    try:
        col = header_values.index(user_id) + 1
    except ValueError:
        await ctx.send(f'{ctx.author.mention} 메모를 찾지 못했어요')
        return

    # Retrieve memo content for the user from row 2
    memo_values = sheet.col_values(col)[1:]

    # Split memo numbers by comma and convert to list of integers
    memo_numbers = memo_numbers.split(',')
    memo_numbers = [int(memo_number.strip()) for memo_number in memo_numbers]

    # Sort memo numbers in descending order to avoid index errors
    memo_numbers.sort(reverse=True)

    # Delete the memo contents from the spreadsheet and shift the remaining memos up
    for memo_number in memo_numbers:
        index_to_delete = memo_number + 1
        remaining_memos = [memo for i, memo in enumerate(memo_values) if i != memo_number]
        for i, memo in enumerate(remaining_memos):
            sheet.update_cell(i+2, col, memo)

        # Clear the last cell after shifting the memos or if the deleted memo is the last one
        sheet.update_cell(len(remaining_memos)+1, col, '')

    await ctx.send(f'{ctx.author.mention} 메모 {", ".join(str(memo_number) for memo_number in memo_numbers)}이(가) 정상적으로 삭제됐어요!')
        
@bot.command(name='전체삭제')
async def delete_all_memos(ctx):
    # Extract user ID
    user_id = str(ctx.author.id)

    # Find the column index of the user ID in row 1
    header_values = sheet.row_values(1)
    try:
        col = header_values.index(user_id) + 1
    except ValueError:
        await ctx.send(f'{ctx.author.mention} 저장된 메모가 없습니다')
        return

    # Delete the entire column for the user
    sheet.delete_columns(col)

    await ctx.send(f'{ctx.author.mention} 모든 메모가 삭제됐어요!')
        
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
    
#-------------------------메뉴추천-------------------------#

class MenuSelector(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.category = None
        self.foods = {
            "분식": ["김밥", "라면", "떡볶이", "튀김", "순대", "만두", "라볶이", "어묵", "소떡소떡", "핫도그", "떡국", "잔치국수", "볶음밥"],
            "한식": ["비빔밥", "불고기", "된장찌개", "김치찌개", "제육볶음", "족발", "부침개", "곱창", "보쌈", "치킨!!", "생선구이", "비빔밥", "쌈밥", "게장", "불고기"],
            "중식": ["짜장면", "짬뽕", "탕수육", "양장피", "마라탕", "마라샹궈", "양꼬치", "깐쇼새우", "깐풍기"],
            "일식": ["초밥", "우동", "돈까스", "라멘", "회", "타코야끼", "샤브샤브"],
            "양식": ["피자", "파스타", "스테이크", "샐러드", "햄버거", "바베큐", "그라탕"],
            "해장": ["우거지국", "홍합탕", "순대국", "콩나물국밥", "뼈해장국", "대파라면", "선지해장국", "매생이국", "북엇국"],
            "디저트": ["아이스크림", "빵", "과일", "케이크", "마카롱", "요거트", "와플"],
            "편의점": ["삼각김밥", "도시락", "샌드위치", "컵라면", "컵밥", "라이스바"],
            "기타": ["월남쌈", "나시고랭", "브리또", "케밥", "맥앤치즈", "분짜", "쌀국수"],
        }
        self.menu_select = discord.ui.Select(
            placeholder="원하시는 종류를 선택해주세요!",
            options=[
                discord.SelectOption(label="분식", value="분식"),
                discord.SelectOption(label="한식", value="한식"),
                discord.SelectOption(label="중식", value="중식"),
                discord.SelectOption(label="일식", value="일식"),
                discord.SelectOption(label="양식", value="양식"),
                discord.SelectOption(label="해장", value="해장"),
                discord.SelectOption(label="디저트", value="디저트"),
                discord.SelectOption(label="편의점", value="편의점"),
                discord.SelectOption(label="기타", value="기타"),
            ],
        )
        self.menu_select.callback = self.select_callback
        self.add_item(self.menu_select)
        self.recommend_button = discord.ui.Button(label="추천받기!", disabled=True, style=discord.ButtonStyle.primary)
        self.recommend_button.callback = self.recommend_callback
        self.add_item(self.recommend_button)

    async def select_callback(self, interaction: discord.Interaction):
        self.category = interaction.data['values'][0]
        self.recommend_button.disabled = False
        await interaction.response.edit_message(view=self)

    async def recommend_callback(self, interaction: discord.Interaction):
        selected_food = random.choice(self.foods[self.category])
        food = discord.Embed(title=f"{self.category} 추천메뉴", description="아래 추천받기 버튼을 클릭해서 메뉴를 추천받아보세요!", color=0x00ff00)
        food.add_field(name="메뉴", value=f"{selected_food}")
        food.set_footer(text="맛있게 드세요! 🥳")
        food.add_field(name="재학생들의 국내/외 맛집 리스트!", url="https://www.google.com/maps/d/edit?mid=1-le8EVMGB6tH-4ryziNUUub1XyOSgHI&usp=sharing")
        await interaction.response.edit_message(embed=food, view=self)
        
@bot.command(name='메뉴추천')
async def menu_recommendation(ctx):
    selector_view = MenuSelector()
    message = await ctx.send("원하시는 종류를 선택해주세요!", view=selector_view)
    selector_view.message = message
    
#Run the bot
bot.run(TOKEN)
