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
import gspread.exceptions
import re
import pytz
import gspread_asyncio
import asyncio
import discord.ui as ui
import time

from google.oauth2.service_account import Credentials
from datetime import date, timedelta
from datetime import datetime
from discord import Embed
from discord import Interaction
from discord.ext import tasks, commands
from discord.ext.commands import Context
from discord.utils import get
from urllib.request import Request
from discord.ui import Select, Button, View

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.typing = False
intents.presences = False


bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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

credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
aio_creds = credentials

#------------------------------------------------#

# Set up Google Sheets worksheet
async def get_sheet2():
    client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: aio_creds)
    client = await client_manager.authorize()
    spreadsheet = await client.open('서버기록')
    sheet2 = await spreadsheet.worksheet('일취월장')
    rows = await sheet2.get_all_values()
    return sheet2, rows 

async def find_user(username, sheet):
    cell = None
    try:
        cells = await sheet.findall(username)
        if cells:
            cell = cells[0]
    except gspread.exceptions.APIError as e:
        print(f'find_user error: {e}')
    return cell

class CustomSelect1(discord.ui.Select):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "인증":
            await interaction.response.send_message("'!인증 해당날짜' 명령어를 통해 해당날짜의 일취월장 인증을 할 수 있습니다 예시)!인증 0101", ephemeral=True)
        elif self.values[0] == "누적":
            await interaction.response.send_message("'누적' 명령어를 통해 일취월장 이번 주 인증횟수와 전체 랭킹 누적현황을 알 수 있습니다 예시)!누적", ephemeral=True)
            
@bot.command(name="일취월장")
async def qu(ctx):
    await ctx.message.delete()  # 명령어 삭제
    
    embed = discord.Embed(title="일취월장 명령어 모음집", description=f"{ctx.author.mention}님 원하시는 명령어를 아래에서 골라주세요")
    embed.set_footer(text="이 창은 1분 후 자동 삭제됩니다")

    message = await ctx.send(embed=embed, ephemeral=True)

    select = CustomSelect(
        options=[
            discord.SelectOption(label="인증", value="인증"),
            discord.SelectOption(label="누적", value="누적")
        ],
        placeholder="명령어를 선택하세요",
        min_values=1,
        max_values=1
    )

    select_container = discord.ui.View()
    select_container.add_item(select)

    message = await message.edit(embed=embed, view=select_container)

    await asyncio.sleep(60)  # 1분 대기
    await message.delete()  # 임베드 메시지와 셀렉트 메뉴 삭제
    
class AuthButton(discord.ui.Button):
    def __init__(self, ctx, user, date):
        super().__init__(style=discord.ButtonStyle.green, label="확인")
        self.ctx = ctx
        self.user = user
        self.date = date
        self.stop_loop = False  # Add the stop_loop attribute
    
    async def callback(self, interaction: discord.Interaction):
        
        sheet2, rows = await get_sheet2()
        
        if interaction.user == self.ctx.author:
            return
        existing_users = await sheet2.col_values(1)
        if str(self.user) not in existing_users:
            empty_row = len(existing_users) + 1
            await sheet2.update_cell(empty_row, 1, str(self.user))
            existing_dates = await sheet2.row_values(1)
            if self.date not in existing_dates:
                empty_col = len(existing_dates) + 1
                await sheet2.update_cell(1, empty_col, self.date)
                await sheet2.update_cell(empty_row, empty_col, "1")
            else:
                col = existing_dates.index(self.date) + 1
                await sheet2.update_cell(empty_row, col, "1")
        else:
            index = existing_users.index(str(self.user)) + 1
            existing_dates = await sheet2.row_values(1)
            if self.date not in existing_dates:
                empty_col = len(existing_dates) + 1
                await sheet2.update_cell(1, empty_col, self.date)
                await sheet2.update_cell(index, empty_col, "1")
            else:
                col = existing_dates.index(self.date) + 1
                await sheet2.update_cell(index, col, "1")
        await interaction.message.edit(embed=discord.Embed(title="인증상황", description=f"{interaction.user.mention}님이 {self.ctx.author.mention}의 {self.date} 일취월장을 인증했습니다🥳"), view=None)
        self.stop_loop = True

class CancelButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(style=discord.ButtonStyle.red, label="취소 ")
        self.ctx = ctx
        self.stop_loop = False  # Add the stop_loop attribute
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.author.id != self.ctx.author.id:
            await interaction.message.delete()
            self.stop_loop = True

async def update_embed(ctx, date, msg):
    button = AuthButton(ctx, ctx.author, date) # Move button creation outside of the loop
    cancel = CancelButton(ctx)  # Create a CancelButton instance
    while True:
        try:
            if button.stop_loop or cancel.stop_loop: # Check if any button's stop_loop is True before updating the message
                break

            view = discord.ui.View(timeout=None)
            view.add_item(button)
            view.add_item(cancel)  # Add the CancelButton to the view

            embed = discord.Embed(title="인증요청", description=f"{ctx.author.mention}님의 {date} 일취월장 인증입니다")
            await msg.edit(embed=embed, view=view)
            await asyncio.sleep(60)
        except discord.errors.NotFound:
            break
        
@bot.command(name='인증')
async def Authentication(ctx, date):
    
    # Validate the input date
    if not re.match(r'^(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])$', date ):
        await ctx.send("정확한 네자리 숫자를 입력해주세요! 1월1일 인증을 하시려면 0101을 입력하시면 됩니다 :)")
        return
    
    sheet2, rows = await get_sheet2()
    existing_users = await sheet2.col_values(1)
    if str(ctx.author) in existing_users:
        user_index = existing_users.index(str(ctx.author)) + 1
        existing_dates = await sheet2.row_values(1)
        if date in existing_dates:
            date_index = existing_dates.index(date) + 1
            cell_value = await sheet2.cell(user_index, date_index)
            if cell_value.value == "1":
                await ctx.send(embed=discord.Embed(title="Authorization Status", description=f"{ctx.author.mention}님, 해당 날짜는 이미 인증되었습니다!"))
                return

    embed = discord.Embed(title="인증상태", description=f"{ctx.author.mention}님의 {date} 일취월장 인증 요청입니다")
    view = discord.ui.View()
    button = AuthButton(ctx, ctx.author, date)
    view.add_item(button)
    view.add_item(CancelButton(ctx)) # Add the CancelButton to the view
    msg = await ctx.send(embed=embed, view=view)
    
    asyncio.create_task(update_embed(ctx, date, msg))

    def check(interaction: discord.Interaction):
        return interaction.message.id == msg.id and interaction.data.get("component_type") == discord.ComponentType.button.value

    await bot.wait_for("interaction", check=check)
   
    
def get_week_range(): 
    today = date.today() # 오늘 날짜 
    monday = today - timedelta(days=today.weekday()) #현재 날짜에서 오늘만큼의 요일을 빼서 월요일 날짜 득획득
    sunday = monday + timedelta(days=6)
    return monday, sunday

    
@bot.command(name='누적')
async def accumulated_auth(ctx):
    sheet2, rows = await get_sheet2()
    existing_users = await sheet2.col_values(1)
    
    if str(ctx.author) not in existing_users:
        await ctx.send(f"{ctx.author.mention}님, 일취월장 기록이 없습니다")
        return

    user_index = existing_users.index(str(ctx.author)) + 1
    total = 0
    monday, sunday = get_week_range()
    existing_dates = await sheet2.row_values(1)
    for date in existing_dates:
        if date and monday.strftime('%m%d') <= date <= sunday.strftime('%m%d'):
            date_index = existing_dates.index(date) + 1
            cell_value = await sheet2.cell(user_index, date_index)
            if cell_value.value:
                total += int(cell_value.value)
    
    overall_ranking = await sheet2.cell(user_index, 2) # Read the value of column B
    overall_ranking_value = int(overall_ranking.value)
    
    embed = discord.Embed(title="누적 인증 현황", description=f"{ctx.author.mention}님, 이번 주({monday.strftime('%m%d')}~{sunday.strftime('%m%d')}) 누적 인증은 {total}회 입니다.\n한 주에 5회 이상 인증하면 랭커로 등록됩니다!\n랭커 누적 횟수는 {overall_ranking_value}회 입니다.")
    
    if overall_ranking_value >= 10 and not discord.utils.get(ctx.author.roles, id=1040094410488172574):
        role = ctx.guild.get_role(1040094410488172574)
        await ctx.author.add_roles(role)
        embed.add_field(name="축하합니다!", value=f"{role.mention} 롤을 획득하셨습니다!")

    if overall_ranking_value >= 30 and not discord.utils.get(ctx.author.roles, id=1040094943722606602):
        role = ctx.guild.get_role(1040094943722606602)
        await ctx.author.add_roles(role)
        embed.add_field(name="축하합니다!", value=f"{role.mention} 롤을 획득하셨습니다!")

    await ctx.send(embed=embed)

#------------------------------------------------#
# Set up Google Sheets worksheet
async def get_sheet3():  # 수정
    client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: aio_creds)
    client = await client_manager.authorize()
    spreadsheet = await client.open('서버기록')
    sheet3 = await spreadsheet.worksheet('랜덤미션')
    rows = await sheet3.get_all_values()
    return sheet3, rows 

async def find_user(username, sheet):
    cell = None
    try:
        cells = await sheet.findall(username)
        if cells:
            cell = cells[0]
    except gspread.exceptions.APIError as e:
        print(f'find_user error: {e}')
    return cell

  
class CustomSelect(discord.ui.Select):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "등록":
            await interaction.response.send_message("'!등록' 명령어를 통해 랜덤미션스터디에 등록할 수 있습니다 예시)!등록", ephemeral=True)
        elif self.values[0] == "뽑기":
            await interaction.response.send_message("'!뽑기' 명령어를 통해 50가지 랜덤 미션 중 하나를 뽑을 수 있어요 예시)!뽑기", ephemeral=True)
        elif self.values[0] == "미션누적":
            await interaction.response.send_message("'미션누적' 명령어를 통해 랜덤미션을 몇 회 인증받았는지 확인할 수 있습니다! 6회 이상 인증 확인되면 완주자 역할을 소유하게 됩니다 예시)!미션누적", ephemeral=True)
            
@bot.command(name="랜덤미션")
async def one_per_day(ctx):
    await ctx.message.delete()  # 명령어 삭제
    
    embed = discord.Embed(title="랜덤미션스터디 명령어 모음집", description=f"{ctx.author.mention}님 원하시는 명령어를 아래에서 골라주세요")
    embed.set_footer(text="이 창은 1분 후 자동 삭제됩니다")

    message = await ctx.send(embed=embed, ephemeral=True)

    select = CustomSelect(
        options=[
            discord.SelectOption(label="등록", value="등록"),
            discord.SelectOption(label="뽑기", value="뽑기"),
            discord.SelectOption(label="미션누적", value="미션누적")
        ],
        placeholder="명령어를 선택하세요",
        min_values=1,
        max_values=1
    )

    select_container = discord.ui.View()
    select_container.add_item(select)

    message = await message.edit(embed=embed, view=select_container)

    await asyncio.sleep(60)  # 1분 대기
    await message.delete()  # 임베드 메시지와 셀렉트 메뉴 삭제
    
@bot.command(name='등록')
async def Register(ctx):
    username = str(ctx.message.author)
    
    sheet3, rows = await get_sheet3()

    # Check if the user is already registered
    registered = False
    row = 2
    while (cell_value := (await sheet3.cell(row, 1)).value):
        if cell_value == username:
            registered = True
            break
        row += 1

    if registered:
        embed = discord.Embed(description=f"{ctx.author.mention}님, 이미 등록하셨어요!", color=0xFF0000)
        await ctx.send(embed=embed)
    else:
        await sheet3.update_cell(row, 1, username)

        role = discord.utils.get(ctx.guild.roles, id=1093781563508015105)
        await ctx.author.add_roles(role)

        embed = discord.Embed(description=f"{ctx.author.mention}님, 랜덤미션스터디에 정상적으로 등록됐습니다!",
                              color=0x00FF00)
        await ctx.send(embed=embed)
    
class RandomMissionView(View):
    def __init__(self, ctx: Context, message: discord.Message):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.message = message

    @discord.ui.button(label='다시 뽑기')
    async def random_mission_button(self, button: Button, interaction: discord.Interaction):
        await self.message.delete()
        await self.ctx.invoke(self.ctx.bot.get_command('再次'))


cooldowns = {}  # Create a dictionary to store cooldowns

@bot.command(name='뽑기')
async def RandomMission(ctx):
    user_id = ctx.author.id
    cooldown_time = 3600  # One hour in seconds

    # Check if the user is not in cooldowns or their cooldown has expired
    if user_id not in cooldowns or cooldowns[user_id] < time.time():
        cooldowns[user_id] = time.time() + cooldown_time

        required_role = discord.utils.get(ctx.guild.roles, id=1093781563508015105)
        allowed_channel_ids = ["1093780375890825246", "922426434633478194", "1057267651405152256"]
        if required_role in ctx.author.roles:
            if str(ctx.channel.id) in allowed_channel_ids:
                await lottery(ctx)
            else:
                await ctx.send("이 채널에서는 사용할 수 없는 명령입니다")
        else:
            embed = discord.Embed(description="랜덤미션스터디 참여자만 !미션 명령어를 사용할 수 있어요", color=0xff0000)
            await ctx.send(embed=embed)

        await asyncio.sleep(cooldown_time)  # Add a delay between command uses

    else:
        # Send the message if the user is still in cooldown
        embed = discord.Embed(description="해당 명령어는 한 시간에 한 번만 쓸 수 있어요!", color=0xff0000)
        await ctx.send(embed=embed)


async def lottery(ctx):
    choices = [('3일간 학습한 내용 요약정리하기', '★★★★★', '<#1098477575778599022>'), ('가장 어려웠던 문장 5번 써보기', '★★★', '<#1098477575778599022>'),
               ('가장 어려웠던 문장 4번 써보기', '★★', '<#1098477575778599022>'),
               ('가장 어려웠던 문장 3번 써보기', '★★', '<#1098477575778599022>'), ('가장 어려웠던 문장 2번 써보기', '★', '<#1098477575778599022>'), ('가장 어려웠던 문장 1번 써보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 30분 학습하기', '★★★', '<#1014721717320560713>'), ('고독한 외국어방에 한 문장 남기기', '★', '<#1014721717320560713>'),
               ('고독한 외국어방에 국가 이모지 입력해서 번역기능 사용해보기', '★', '<#1088639136048619580>'), ('조용한 독서실에서 15분 학습하기', '★', '<#1014721717320560713>'), ('자유게시판 아무 게시판에 가서 댓글 남기기', '★', '<#1056759327668588625>'), 
               ('나만의 학습노트 공유하기 ', '★★★★★', '<#1098477575778599022>'), ('수다챗에 한마디 남기기', '★', '<#922501708175769640>'), ('!운세 입력해서 올해의 외국어 운세보기', '★', '<#1098477575778599022>'), ('학습중인 언어권 노래 하나 추천하기', '★★', '<#1098477575778599022>'), 
               ('학습하는 언어권 문화 한 개 찾아서 공유하기', '★', '<#1098477575778599022>'), ('오늘은 통과!', '★', '없음!'), ('오운완 인증 글 올리기', '★★★★★', '<#1034639972503928863>'), ('올해 외국어 학습목표 써보기', '★', '<#1098477575778599022>'), ('내 책상 위 물건 중 하나 외국어로 적어보기', '★★', '<#1098477575778599022>'),
               ('본인이 가장 좋아하는 영화 제목 학습하는 언어버전으로 적어보기', '★★★', '<#1098477575778599022>'), ('일취월장에 오늘 학습내용 인증하기', '★★★', '<#1098477575778599022>'), ('조용한 독서실에서 15분 학습하기', '★', '<#1014721717320560713>'), ('이번주 학습목표 써보기', '★', '<#1098477575778599022>'), 
               ('학습하는 언어권 명언 찾아서 공유하기', '★★', '<#1098477575778599022>'), ('축! 커피 교환권 당첨! 일대일문의를 통해 글 남겨주세요!', '♥♥♥', '<#1057131667250237460>'), ('출석부에 출석체크 완료하기', '★', '<#1064847315350855730>'), 
               ('좋아하는 단어 본인이 학습하는 언어로  두 개 쓰기', '★', '<#1098477575778599022>'), ('좋아하는 단어 본인이 학습하는 언어로 한 개 쓰기', '★', '<#1098477575778599022>'), ('내 가방 속 물건 중 한 개 학습하는 언어로 써서 공유하기', '★★', '<#1098477575778599022>'), ('보이는 독서실에서 쫓겨나보기', '★', '<#1014721859188699216>'), ('내가 학습중인 언어로 자기소개 작성해서 공유하기', '★★★★', '<#1098477575778599022>'), 
               ('!MBTI 명령어를 입력해서 외국어 MBTI 보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 60분 학습하기', '★★★★★', '<#1014721717320560713>'), ('학습하는 언어권 명언 찾아서 필사 후 사진 찍어 공유하기', '★★★', '<#1098477575778599022>'), ('외우기 힘들었던 단어 한 개 써보기', '★', '<#1098477575778599022>'),
               ('외우기 힘들었던 단어 두 개 써보기', '★★', '<#1098477575778599022>'), ('외우기 힘들었던 단어 세 개 써보기', '★★★', '<#1098477575778599022>'), ('좋아하는 브랜드 명 본인이 학습하는 언어로 한 번 써보기', '★★', '<#1098477575778599022>'), ('!메뉴추천 써보기', '★', '<#1098477575778599022>'), ('다른 학습자의 랜덤미션 인증버튼 눌러주기', '★', '<#1098477575778599022>'), 
               ('학습하는 언어권 노래 듣고 아는 단어 찾아서 공유하기', '★★★★', '<#1098477575778599022>'), ('가장 좋아하는 외국어 문장 한 번 써보기', '★', '<#1098477575778599022>'), ('가장 좋아하는 외국어 문장 세 번 써보기', '★★★', '<#1098477575778599022>'), ('!역할 입력해서 내가 가진 역할 확인해보기', '★', '<#1098477575778599022>'), 
               ('학습중인 언어로 세 줄 일기 써서 공유하기', '★★★★', '<#1098477575778599022>'), ('!공부 입력해보기', '★', '<#1098477575778599022>'), ('일취월장 채널의 다른 학습자 인증에 격려 댓글 남겨주기', '★★★★', '<#978952156617007114>'),
               ('일취월장 채널의 다른 학습자 인증을 보고 격려 메시지 작성하기', '★★', '<#1098477575778599022>'), ('꼭 가보고 싶은 도시 학습하는 언어로 적어보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 한 시간 이상 참여 후 커피 교환하기! 이미 받으신 분도 가능! 참여 방법이 궁금하시다면 물어봐 주세요!', '★', '<#1014721717320560713>')]

    embed = discord.Embed(description=f'{ctx.author.mention}님의 미션을 뽑는 중입니다', color=0xff0000)
    message = await ctx.send(embed=embed)
    message_id = message.id
    selected_choices = random.sample(choices, 10)

    for i, (choice, difficulty, location) in enumerate(selected_choices):
        embed.clear_fields()
        embed.add_field(name=f'미션', value=choice, inline=True)
        embed.add_field(name='난이도', value=difficulty, inline=True)
        embed.add_field(name='미션수행장소', value=location, inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)

    result, difficulty, location = random.choice(selected_choices)
    embed.description = f"{ctx.author.mention}님의 오늘의 미션입니다!"
    embed.clear_fields()
    embed.add_field(name='오늘의 미션', value=result, inline=False)
    embed.add_field(name='난이도', value=difficulty, inline=False)
    embed.add_field(name='미션수행장소', value=location, inline=False)
    embed.set_footer(text='한 번 더 뽑아보시겠어요?')

    view = RandomMissionView(ctx, message)
    message = await message.edit(embed=embed, view=view)

@bot.command(name='再次')
async def Relottery(ctx):
    choices = [('3일간 학습한 내용 요약정리하기', '★★★★★', '<#1098477575778599022>'), ('가장 어려웠던 문장 5번 써보기', '★★★', '<#1098477575778599022>'),
               ('가장 어려웠던 문장 4번 써보기', '★★', '<#1098477575778599022>'),
               ('가장 어려웠던 문장 3번 써보기', '★★', '<#1098477575778599022>'), ('가장 어려웠던 문장 2번 써보기', '★', '<#1098477575778599022>'), ('가장 어려웠던 문장 1번 써보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 30분 학습하기', '★★★', '<#1014721717320560713>'), ('고독한 외국어방에 한 문장 남기기', '★', '<#1014721717320560713>'),
               ('고독한 외국어방에 국가 이모지 입력해서 번역기능 사용해보기', '★', '<#1088639136048619580>'), ('조용한 독서실에서 15분 학습하기', '★', '<#1014721717320560713>'), ('자유게시판 아무 게시판에 가서 댓글 남기기', '★', '<#1056759327668588625>'), 
               ('나만의 학습노트 공유하기 ', '★★★★★', '<#1098477575778599022>'), ('수다챗에 한마디 남기기', '★', '<#922501708175769640>'), ('!운세 입력해서 올해의 외국어 운세보기', '★', '<#1098477575778599022>'), ('학습중인 언어권 노래 하나 추천하기', '★★', '<#1098477575778599022>'), 
               ('학습하는 언어권 문화 한 개 찾아서 공유하기', '★', '<#1098477575778599022>'), ('오늘은 통과!', '★', '없음!'), ('오운완 인증 글 올리기', '★★★★★', '<#1034639972503928863>'), ('올해 외국어 학습목표 써보기', '★', '<#1098477575778599022>'), ('내 책상 위 물건 중 하나 외국어로 적어보기', '★★', '<#1098477575778599022>'),
               ('본인이 가장 좋아하는 영화 제목 학습하는 언어버전으로 적어보기', '★★★', '<#1098477575778599022>'), ('일취월장에 오늘 학습내용 인증하기', '★★★', '<#1098477575778599022>'), ('조용한 독서실에서 15분 학습하기', '★', '<#1014721717320560713>'), ('이번주 학습목표 써보기', '★', '<#1098477575778599022>'), 
               ('학습하는 언어권 명언 찾아서 공유하기', '★★', '<#1098477575778599022>'), ('축! 커피 교환권 당첨! 일대일문의를 통해 글 남겨주세요!', '♥♥♥', '<#1057131667250237460>'), ('출석부에 출석체크 완료하기', '★', '<#1064847315350855730>'), 
               ('좋아하는 단어 본인이 학습하는 언어로  두 개 쓰기', '★', '<#1098477575778599022>'), ('좋아하는 단어 본인이 학습하는 언어로 한 개 쓰기', '★', '<#1098477575778599022>'), ('내 가방 속 물건 중 한 개 학습하는 언어로 써서 공유하기', '★★', '<#1098477575778599022>'), ('보이는 독서실에서 쫓겨나보기', '★', '<#1014721859188699216>'), ('내가 학습중인 언어로 자기소개 작성해서 공유하기', '★★★★', '<#1098477575778599022>'), 
               ('!MBTI 명령어를 입력해서 외국어 MBTI 보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 60분 학습하기', '★★★★★', '<#1014721717320560713>'), ('학습하는 언어권 명언 찾아서 필사 후 사진 찍어 공유하기', '★★★', '<#1098477575778599022>'), ('외우기 힘들었던 단어 한 개 써보기', '★', '<#1098477575778599022>'),
               ('외우기 힘들었던 단어 두 개 써보기', '★★', '<#1098477575778599022>'), ('외우기 힘들었던 단어 세 개 써보기', '★★★', '<#1098477575778599022>'), ('좋아하는 브랜드 명 본인이 학습하는 언어로 한 번 써보기', '★★', '<#1098477575778599022>'), ('!메뉴추천 써보기', '★', '<#1098477575778599022>'), ('다른 학습자의 랜덤미션 인증버튼 눌러주기', '★', '<#1098477575778599022>'), 
               ('학습하는 언어권 노래 듣고 아는 단어 찾아서 공유하기', '★★★★', '<#1098477575778599022>'), ('가장 좋아하는 외국어 문장 한 번 써보기', '★', '<#1098477575778599022>'), ('가장 좋아하는 외국어 문장 세 번 써보기', '★★★', '<#1098477575778599022>'), ('!역할 입력해서 내가 가진 역할 확인해보기', '★', '<#1098477575778599022>'), 
               ('학습중인 언어로 세 줄 일기 써서 공유하기', '★★★★', '<#1098477575778599022>'), ('!공부 입력해보기', '★', '<#1098477575778599022>'), ('일취월장 채널의 다른 학습자 인증에 격려 댓글 남겨주기', '★★★★', '<#978952156617007114>'),
               ('일취월장 채널의 다른 학습자 인증을 보고 격려 메시지 작성하기', '★★', '<#1098477575778599022>'), ('꼭 가보고 싶은 도시 학습하는 언어로 적어보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 한 시간 이상 참여 후 커피 교환하기! 이미 받으신 분도 가능! 참여 방법이 궁금하시다면 물어봐 주세요!', '★', '<#1014721717320560713>')]

    embed = discord.Embed(description=f'{ctx.author.mention}님의 미션을 다시 뽑는 중입니다', color=0xff0000)
    message = await ctx.send(embed=embed)
    message_id = message.id
    selected_choices = random.sample(choices, 10)

    for i, (choice, difficulty, location) in enumerate(selected_choices):
        embed.clear_fields()
        embed.add_field(name=f'미션', value=choice, inline=True)
        embed.add_field(name='난이도', value=difficulty, inline=True)
        embed.add_field(name='미션수행장소', value=location, inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)

    result, difficulty, location = random.choice(selected_choices)
    embed.description = f"{ctx.author.mention}님의 오늘의 미션입니다!"
    embed.clear_fields()
    embed.add_field(name='오늘의 임무', value=result, inline=False)
    embed.add_field(name='난이도', value=difficulty, inline=False)
    embed.add_field(name='미션수행장소', value=location, inline=False)
    message = await message.edit(embed=embed)

kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst).replace(tzinfo=None)
today1 = now.strftime('%m%d')    
    
@bot.command(name='미션인증')
async def random_mission_auth(ctx):
    sheet3, rows = await get_sheet3()  # get_sheet3 호출 결과값 받기
    username = str(ctx.message.author)

    now = datetime.now()  # 날짜 업데이트 코드 수정
    today1 = now.strftime('%m%d')

    user_row = None
    for row in await sheet3.get_all_values():
        if username in row:
            user_row = row
            break

    if user_row is None:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    user_cell = await find_user(username, sheet3)

    if user_cell is None:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    today1_col = None
    for i, col in enumerate(await sheet3.row_values(1)):
        if today1 in col:
            today1_col = i + 1
            break

    if today1_col is None:
        embed = discord.Embed(title='Error', description='랜덤미션스터디 기간이 아닙니다')
        await ctx.send(embed=embed)
        return

    if (await sheet3.cell(user_cell.row, today1_col)).value == '1':
        embed = discord.Embed(title='Error', description='이미 오늘의 미션 인증을 하셨습니다')
        await ctx.send(embed=embed)
        return
      
    # create and send the message with the button
    embed = discord.Embed(title="미션 인증", description=f' 버튼을 눌러 {ctx.author.mention}님의 미션을 인증해주세요')
    button = AuthButton2(ctx, username, today1, sheet3)
    view = discord.ui.View()
    view.add_item(button)
    await update_embed_auth(ctx, username, today1, sheet3)
        
class AuthButton2(discord.ui.Button):
    def __init__(self, ctx, username, sheet3):
        super().__init__(style=discord.ButtonStyle.green, label="미션인증")
        self.ctx = ctx
        self.username = username
        self.sheet3 = sheet3
        self.auth_event = asyncio.Event()
        self.stop_loop = False

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            # If the user is the button creator, send an error message
            embed = discord.Embed(title='Error', description='자신이 생성한 버튼은 사용할 수 없습니다 :(')
            await interaction.response.edit_message(embed=embed, view=None)
            return

        try:
            user_cell = await find_user(self.username, self.sheet3)
            if user_cell is None:
                embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
                await interaction.response.edit_message(embed=embed, view=None)
                return
            user_row = user_cell.row
        except gspread.exceptions.CellNotFound:
            embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
            await interaction.response.edit_message(embed=embed, view=None)
            return

        now = datetime.now()
        self.today = now.strftime('%m%d')

        # Authenticate the user in the spreadsheet
        today1_col = (await self.sheet3.find(self.today)).col
        await self.sheet3.update_cell(user_row, today1_col, '1')

        # Set the auth_event to stop the loop
        self.auth_event.set()

        # Remove the button from the view
        self.view.clear_items()

        # Send a success message
        await interaction.message.edit(embed=discord.Embed(title="인증완료!", description=f"{interaction.user.mention}님이 {self.ctx.author.mention}의 랜덤미션을 인증했습니다🥳"), view=None)
        self.stop_loop = True

async def update_embed_auth(ctx, username, sheet3):
    embed = discord.Embed(title="미션 인증", description=f' 버튼을 눌러 {ctx.author.mention}님의 미션을 인증해주세요')
    button = AuthButton2(ctx, username, sheet3)
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    message = await ctx.send(embed=embed, view=view)

    while not button.stop_loop:
        await asyncio.sleep(60)
        now = datetime.now()
        today1 = now.strftime('%m%d')
        if not button.stop_loop:
            view = discord.ui.View(timeout=None)
            button = AuthButton2(ctx, username, sheet3)
            view.add_item(button)
            await message.edit(embed=embed, view=view)

    view.clear_items()
    await message.edit(view=view)
            
@bot.command(name='미션누적')
async def mission_count(ctx):
    username = str(ctx.message.author)
    sheet3, rows = await get_sheet3()
    
    # Find the user's row in the Google Sheet
    user_row = None
    for row in await sheet3.get_all_values():
        if username in row:
            user_row = row
            break

    if user_row is None:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    user_cell = await sheet3.find(username)
    count = int((await sheet3.cell(user_cell.row, 9)).value)  # Column I is the 9th column

    # Send the embed message with the user's authentication count
    embed = discord.Embed(description=f"{ctx.author.mention}님은 {count} 회 인증하셨어요!", color=0x00FF00)
    await ctx.send(embed=embed)

    # Check if the user's count is 6 or 7 and grant the Finisher role
    if count in [6, 7]:
        role = discord.utils.get(ctx.guild.roles, id=1093831438475989033)
        await ctx.author.add_roles(role)
        embed = discord.Embed(description="완주를 축하드립니다! 완주자 롤을 받으셨어요!", color=0x00FF00)
        await ctx.send(embed=embed)
        
#------------------------------------------------#

# Set up Google Sheets worksheet
async def get_sheet1():
    client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: aio_creds)
    client = await client_manager.authorize()
    spreadsheet = await client.open('서버기록')
    sheet1 = await spreadsheet.worksheet('고정')
    rows = await sheet1.get_all_values()
    return sheet1, rows 
  
sticky_messages = {}
last_sticky_messages = {} 
    
def has_specific_roles(allowed_role_ids):
    async def predicate(ctx):
        allowed_roles = [ctx.guild.get_role(role_id) for role_id in allowed_role_ids]
        return any(role in ctx.author.roles for role in allowed_roles)

    return commands.check(predicate)

allowed_role_ids = [1019164281696174180, 922400231549722664]    
    
# 스프레드시트에서 초기 고정 메시지를 가져옵니다.
async def refresh_sticky_messages(sheet1):
    global sticky_messages
    global last_sticky_messages
    sheet1_values = await sheet1.get_all_values()

    new_sticky_messages = {}
    for row in sheet1_values:
        if len(row) == 2 and row[0].isdigit():
            channel_id = int(row[0])
            message = row[1]
            new_sticky_messages[channel_id] = message

    deleted_channel_ids = set(sticky_messages.keys()) - set(new_sticky_messages.keys())
    for channel_id in deleted_channel_ids:
        if channel_id in last_sticky_messages:
            old_message = last_sticky_messages[channel_id]
            try:
                asyncio.create_task(old_message.delete())
            except discord.NotFound:
                pass

    sticky_messages = new_sticky_messages
    
@bot.command(name='고정')
@has_specific_roles(allowed_role_ids)
async def sticky(ctx, *, message):
    global sticky_messages
    channel_id = ctx.channel.id
    sticky_messages[channel_id] = message

    # 스프레드시트에 고정 메시지를 저장합니다.
    sheet1, _ = await get_sheet1()
    if str(channel_id) in await sheet1.col_values(1):
        row_num = (await sheet1.col_values(1)).index(str(channel_id)) + 1
    else:
        row_num = len(await sheet1.col_values(1)) + 1

    await sheet1.update_cell(row_num, 1, str(channel_id))
    await sheet1.update_cell(row_num, 2, message)

    # 스프레드시트에 저장된 내용을 업데이트합니다.
    await refresh_sticky_messages(sheet1)

    await ctx.send(f'메시지가 고정됐습니다!')

@bot.command(name='해제')
@has_specific_roles(allowed_role_ids)
async def unsticky(ctx):
    global sticky_messages
    channel_id = ctx.channel.id

    if channel_id in sticky_messages:
        del sticky_messages[channel_id]

        # 스프레드시트에서 고정 메시지를 삭제합니다.
        sheet1, _ = await get_sheet1()
        row_num = (await sheet1.col_values(1)).index(str(channel_id)) + 1
        await sheet1.delete_row(row_num)

        # 스프레드시트에 저장된 내용을 업데이트합니다.
        await refresh_sticky_messages(sheet1)

        await ctx.send('고정이 해제됐어요!')
    else:
        await ctx.send('이 채널에는 고정된 메시지가 없어요')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    global sticky_messages
    global last_sticky_messages

    channel_id = message.channel.id

    if channel_id in sticky_messages:
        if channel_id in last_sticky_messages:
            old_message = last_sticky_messages[channel_id]
            try:
                await old_message.delete()
            except discord.NotFound:
                pass

        new_message = await message.channel.send(sticky_messages[message.channel.id])
        last_sticky_messages[message.channel.id] = new_message
    
#------------------------------------------------#    

        
#Run the bot
bot.run(TOKEN)
