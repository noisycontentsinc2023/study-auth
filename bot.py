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
import googletrans 
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
SECRET = os.environ['SECRET']

translator = googletrans.Translator()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.typing = False
intents.presences = False

private_key = os.environ['SECRET'].replace("\\n", "\n")


bot = commands.Bot(command_prefix=PREFIX, intents=intents)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_info = {
  "type": "service_account",
  "project_id": "server-439817",
  "private_key_id": "45202b8f054ef38af115cf72e0c9d3bed3d8a008",
  "private_key": private_key,
  "client_email": "server@server-439817.iam.gserviceaccount.com",
  "client_id": "100976887028503717064",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/server%40server-439817.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
aio_creds = credentials

#------------------------------------------------#
flag_emoji_dict = {
"🇺🇸": "en",
"🇩🇪": "de",
"🇫🇷": "fr",
"🇪🇸": "es",
"🇮🇹": "it",
"🇵🇹": "pt",
"🇷🇺": "ru",
"🇦🇱": "sq",
"🇸🇦": "ar",
"🇧🇦": "bs",
"🇨🇳": "zh-CN",
"🇹🇷": "tr",
"🇵🇱": "pl",
"🇳🇴": "no",
"🇸🇬": "sv",
"🇯🇵": "ja",
"🇰🇷": "ko",
"🇻🇳": "vi",
"🇮🇩": "id",
}

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']

intents=discord.Intents.all()
prefix = '!'
bot = commands.Bot(command_prefix=prefix, intents=intents)


#------------------------------------------------번역기------------------------------------------------------#
@bot.event
async def on_reaction_add(reaction, user):
  
    # Check if the reaction is a flag emoji
    if reaction.emoji in flag_emoji_dict:
        # Get the language code corresponding to the flag emoji
        lang_code = flag_emoji_dict[reaction.emoji]
        # Get the original message
        message = reaction.message
        # Translate the message to the desired language
        detected_lang = translator.detect(message.content)
        translated_message = translator.translate(message.content, dest=lang_code).text
        pronunciation_message = translator.translate(message.content, dest=lang_code).pronunciation

        embed = Embed(title='번역 translate', description=f'{translated_message}', color=0x00ff00)
        embed.add_field(name="원문 original text", value=message.content, inline=False)
        embed.add_field(name="발음 pronunciation", value=pronunciation_message, inline=False)
       # await reaction.message.channel.send(content=f'{reaction.user.mention}',embed=embed)
        await reaction.message.channel.send(content=f'{user.mention}',embed=embed)
#------------------------------------------------#

# Set up Google Sheets worksheet
async def get_sheet2():
    client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: aio_creds)
    client = await client_manager.authorize()
    spreadsheet = await client.open('서버기록')
    sheet2 = await spreadsheet.worksheet('일취월장2025')
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

async def update_count(sheet2, user):
    existing_users = await sheet2.col_values(1)
    if str(user) not in existing_users:
        empty_row = len(existing_users) + 1
        await sheet2.update_cell(empty_row, 1, str(user))
        await sheet2.update_cell(empty_row, 3, "1")
    else:
        index = existing_users.index(str(user)) + 1
        current_count = await sheet2.cell(index, 3)
        current_value = current_count.value if current_count.value is not None else 0
        new_count = int(current_value) + 1
        await sheet2.update_cell(index, 3, str(new_count))
        
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
        await update_count(sheet2, interaction.user)  # Update the count of the user who clicked the button

class CancelButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(style=discord.ButtonStyle.red, label="취소")
        self.ctx = ctx
        self.stop_loop = False  # Add the stop_loop attribute
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            await interaction.message.delete()
            self.stop_loop = True
        else:
            await interaction.response.send_message("글 작성자만 취소할 수 있습니다", ephemeral=True)

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
    target_channel_id = 978952156617007114

    # If the command is not used in the target channel, ignore it
    if ctx.channel.id != target_channel_id:
        await ctx.send("해당 명령어는 <#978952156617007114> 에서만 사용할 수 있어요")
        return
      
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
    hidden = await sheet2.cell(user_index, 3)
    hidden_value = int(hidden.value)
    
    embed = discord.Embed(title="누적 인증 현황", description=f"{ctx.author.mention}님, 이번 주({monday.strftime('%m%d')}~{sunday.strftime('%m%d')}) 누적 인증은 {total}회 입니다.\n한 주에 5회 이상 인증하면 랭커로 등록됩니다!\n랭커 누적 횟수는 {overall_ranking_value}회 입니다.\n현재까지 총 {hidden_value} 회 다른 학습자의 인증을 도와주셨어요!")
 
    if overall_ranking_value >= 1 and not discord.utils.get(ctx.author.roles, id=1016152041258758217):
        role = ctx.guild.get_role(1016152041258758217)
        await ctx.author.add_roles(role)
        embed.add_field(name="축하합니다!", value=f"{role.mention} 롤을 획득하셨습니다!")
        
    if overall_ranking_value >= 10 and not discord.utils.get(ctx.author.roles, id=1040094410488172574):
        role = ctx.guild.get_role(1040094410488172574)
        await ctx.author.add_roles(role)
        embed.add_field(name="축하합니다!", value=f"{role.mention} 롤을 획득하셨습니다!")

    if overall_ranking_value >= 30 and not discord.utils.get(ctx.author.roles, id=1040094943722606602):
        role = ctx.guild.get_role(1040094943722606602)
        await ctx.author.add_roles(role)
        embed.add_field(name="축하합니다!", value=f"{role.mention} 롤을 획득하셨습니다!")
    
    if overall_ranking_value >= 60 and not discord.utils.get(ctx.author.roles, id=1098176357403471935):
        role = ctx.guild.get_role(1098176357403471935)
        await ctx.author.add_roles(role)
        embed.add_field(name="축하합니다!", value=f"{role.mention} 롤을 획득하셨습니다!")
      
    if overall_ranking_value >= 111 and not discord.utils.get(ctx.author.roles, id=1324788848076787813):
        role = ctx.guild.get_role(1324788848076787813)
        await ctx.author.add_roles(role)
        embed.add_field(name="망령이 나타났다👻", value=f"{role.mention} 롤을 획득하셨습니다!")
      
    if hidden_value >= 100 and not discord.utils.get(ctx.author.roles, id=1105398539951030272):
        role = ctx.guild.get_role(1105398539951030272)
        await ctx.author.add_roles(role)
        embed.add_field(name="축하합니다!", value=f"{role.mention} 롤을 획득하셨습니다!")

    await ctx.send(embed=embed)

#------------------------------------------고정-----------------------------------------------#

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
    
#---------------------필사클럽2505기------------------------#  
#------------------------------------------------#    
async def get_sheet11():  
    client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: aio_creds)
    client = await client_manager.authorize()
    spreadsheet = await client.open('서버기록')
    sheet11 = await spreadsheet.worksheet('필사클럽(2505)')
    rows = await sheet11.get_all_values()
    return sheet11, rows 

async def find_user(username, sheet):
    cell = None
    try:
        cells = await sheet.findall(username)
        print(f"find_user: Searching for {username}. Found: {cells}")  # 디버깅 로그
        if cells:
            cell = cells[0]
    except gspread.exceptions.APIError as e:
        print(f"find_user error: {e}")
    return cell
            
def is_allowed_channel(channel_id):
    allowed_channels = ["1020187965739253760", "1194273995319685120", "1057267651405152256"]
    return str(channel_id) in allowed_channels
  
kst = pytz.timezone('Asia/Seoul') # 한국 시간대로 설정 
now = datetime.now(kst).replace(tzinfo=None)
today3 = now.strftime('%m%d') 

@bot.command(name='')
async def bixie_user(ctx):
    sheet11, rows = await get_sheet11()  # Google Sheets 데이터 가져오기
    username = str(ctx.message.author)

    user_row = next((i for i, row in enumerate(rows) if row[0] == username), None)

    if user_row is not None:
        embed = discord.Embed(title='오류', description=f'{ctx.author.mention}님은 이미 등록된 사용자입니다')
        await ctx.send(embed=embed)
        return

    # 새로운 사용자 추가
    new_user_row = [username] + ["0"] * (len(rows[0]) - 1)
    await sheet11.insert_row(new_user_row, 2)

    # 역할 부여
    role_id = 1363708984636215428
    role = ctx.guild.get_role(role_id)

    if role is not None:
        try:
            await ctx.author.add_roles(role)
            embed = discord.Embed(
                title='등록 완료',
                description=f'{ctx.author.mention}님 필사클럽(2505)에 성공적으로 등록되었습니다\n{role.mention} 역할이 부여되었습니다!'
            )
        except discord.errors.Forbidden:
            embed = discord.Embed(
                title='오류',
                description=f'{ctx.author.mention}님, 봇에 역할 관리 권한이 없습니다. 관리자에게 문의하세요.'
            )
    else:
        embed = discord.Embed(
            title='등록 완료',
            description=f'{ctx.author.mention}님 필사클럽(2505)에 성공적으로 등록되었습니다\n그러나 역할을 찾을 수 없습니다.'
        )

    await ctx.send(embed=embed)

@bot.command(name='필사인증')
async def bixie_auth(ctx):
    required_role_id = 1363708984636215428  # 역할 ID (숫자)
    role = discord.utils.get(ctx.guild.roles, id=required_role_id)

    # 역할이 존재하지 않을 경우
    if role is None:
        embed = discord.Embed(
            title='오류',
            description=f"서버에 '필사클럽(2505)' 역할이 존재하지 않습니다. 관리자에게 문의하세요."
        )
        await ctx.send(embed=embed)
        return

    # 사용자에게 해당 역할이 없는 경우
    if role not in ctx.author.roles:
        embed = discord.Embed(
            title='오류',
            description=f"{ctx.author.mention}님은 필사클럽(2505)에 등록된 멤버가 아닙니다."
        )
        await ctx.send(embed=embed)
        return

    # 역할이 있는 경우 계속 진행
    sheet11, rows = await get_sheet11()  # get_sheet11 호출 결과값 받기
    username = str(ctx.message.author)

    now = datetime.now(kst).replace(tzinfo=None)  # 현재 한국 시간대의 날짜 및 시간 가져오기
    today3 = now.strftime('%m%d')  # 현재 날짜를 계산하여 문자열로 변환

    user_row = None
    for row in await sheet11.get_all_values():
        if username in row:
            user_row = row
            break

    if user_row is None:
        embed = discord.Embed(
            title='오류',
            description=f"{ctx.author.mention}님은 필사클럽(2505)에 등록된 멤버가 아닙니다."
        )
        await ctx.send(embed=embed)
        return

    user_cell = await find_user(username, sheet11)

    if user_cell is None:
        embed = discord.Embed(title='오류', description=f'{ctx.author.mention}님은 필사클럽(2505)에 등록된 멤버가 아닙니다.')
        await ctx.send(embed=embed)
        return

    today3_col = None
    for i, col in enumerate(await sheet11.row_values(1)):
        if today3 in col:
            today3_col = i + 1
            break

    if today3_col is None:
        embed = discord.Embed(title='Error', description=f'{ctx.author.mention}님 현재는 필사클럽(2505) 기간이 아닙니다')
        await ctx.send(embed=embed)
        return

    if (await sheet11.cell(user_cell.row, today3_col)).value == '1':
        embed = discord.Embed(title='오류', description='이미 오늘의 인증을 하셨습니다')
        await ctx.send(embed=embed)
        return
      
    await update_embed_book_auth(ctx, username, today3, sheet11)
        
class AuthButton3(discord.ui.Button):
    def __init__(self, ctx, username, today3, sheet11):
        super().__init__(style=discord.ButtonStyle.green, label="필사클럽 인증")
        self.ctx = ctx
        self.username = username
        self.sheet11 = sheet11
        self.auth_event = asyncio.Event()
        self.stop_loop = False
        self.today3 = today3  # 인스턴스 변수로 today3 저장

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            # If the user is the button creator, send an error message
            embed = discord.Embed(title='Error', description='자신이 생성한 버튼은 사용할 수 없습니다 :(')
            await interaction.response.edit_message(embed=embed, view=None)
            return

        try:
            user_cell = await find_user(self.username, self.sheet11)
            if user_cell is None:
                embed = discord.Embed(title='오류', description=f'{ctx.author.mention}님은 필사클럽(2505)에 등록된 멤버가 아닙니다.')
                await interaction.response.edit_message(embed=embed, view=None)
                return
            user_row = user_cell.row
        except gspread.exceptions.CellNotFound:
            embed = discord.Embed(title='오류', description=f'{ctx.author.mention}님은 필사클럽(2505)에 등록된 멤버가 아닙니다.')
            await interaction.response.edit_message(embed=embed, view=None)
            return

        now = datetime.now(kst).replace(tzinfo=None)  # 날짜 업데이트 코드 수정
        self.today = now.strftime('%m%d')

        # Authenticate the user in the spreadsheet
        today3_col = (await self.sheet11.find(self.today)).col
        await self.sheet11.update_cell(user_row, today3_col, '1')

        # Set the auth_event to stop the loop
        self.auth_event.set()

        # Remove the button from the view
        self.view.clear_items()

        # Send a success message
        await interaction.message.edit(embed=discord.Embed(title="인증완료!", description=f"{interaction.user.mention}님이 {self.ctx.author.mention}의 필사클럽을 인증했습니다👍"), view=None)
        self.stop_loop = True

async def update_embed_book_auth(ctx, username, today3, sheet11):
    embed = discord.Embed(title="학습인증", description=f' 버튼을 눌러 {ctx.author.mention}님의 {today3} 필사클럽을 인증해주세요')
    button = AuthButton3(ctx, username, today3, sheet11)
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    message = await ctx.send(embed=embed, view=view)

    while not button.stop_loop:
        await asyncio.sleep(60)
        now = datetime.now(kst).replace(tzinfo=None)
        today3 = now.strftime('%m%d')
        if not button.stop_loop:
            view = discord.ui.View(timeout=None)
            button = AuthButton3(ctx, username, today3, sheet11)
            view.add_item(button)
            await message.edit(embed=embed, view=view)

    view.clear_items()
    await message.edit(view=view)
            
@bot.command(name='필사누적')
async def bixie_count(ctx):
    if not is_allowed_channel(ctx.channel.id):
        await ctx.send("해당 명령어는 <#1194273995319685120>에서만 사용할 수 있어요")
        return
    username = str(ctx.message.author)
    sheet11, rows = await get_sheet11()
    
    # Find the user's row in the Google Sheet
    user_row = None
    for row in await sheet11.get_all_values():
        if username in row:
            user_row = row
            break

    if user_row is None:
        embed = discord.Embed(title='Error', description=f'{ctx.author.mention}님은 필사클럽(2505)에 등록된 멤버가 아닙니다 \n !필사등록 명령어를 통해 먼저 등록해주세요!')
        await ctx.send(embed=embed)
        return

    user_cell = await sheet11.find(username)
    count = int((await sheet11.cell(user_cell.row, 2)).value)  # Column I is the 9th column

    # Send the embed message with the user's authentication count
    embed = discord.Embed(description=f"{ctx.author.mention}님은 현재까지 {count} 회 인증하셨어요!", color=0x00FF00)
    await ctx.send(embed=embed) 


#------------------------------------------------#

@bot.command(name='가위')
async def rock_paper_scissors(ctx):
    user_choice = '가위'
    await play_game(user_choice, ctx, '✌️')

@bot.command(name='바위')
async def rock_paper_scissors(ctx):
    user_choice = '바위'
    await play_game(user_choice, ctx, '✊')

@bot.command(name='보')
async def rock_paper_scissors(ctx):
    user_choice = '보'
    await play_game(user_choice, ctx, '🖐️')

async def play_game(user_choice, ctx, user_emoji):
    rps = ['가위', '바위', '보']
    bot_choice = random.choice(rps)

    # 가위, 바위, 보에 대응하는 이모지
    rps_emoji = {'가위': '✌️', '바위': '✊', '보': '🖐️'}

    result = None
    if user_choice == bot_choice:
        result = '비겼습니다!'
        color = discord.Color.dark_gray()
        emoji = '🤝'
    elif (user_choice == '가위' and bot_choice == '보') or \
         (user_choice == '바위' and bot_choice == '가위') or \
         (user_choice == '보' and bot_choice == '바위'):
        result = '테이망령이 졌습니다!😭'
        color = discord.Color.green()
        emoji = '🎉'
    else:
        result = '테이망령이 이겼습니다!🥳'
        color = discord.Color.red()
        emoji = '😭'

    embed = discord.Embed(title=f'{user_emoji} 대 {rps_emoji[bot_choice]}', description=result, color=color)
    embed.set_author(name='게임 결과')

    await ctx.send(embed=embed)
    
#------------------------------------------------#

@bot.command(name='MBTI')
async def MBTI(ctx):
    embed = discord.Embed(title="소울메이트 언어를 찾아보자!", description="당신의 외국어 mbti는..?", color=0xffd700)
    embed.set_footer(text="아래 버튼을 클릭하여 외국어 mbti를 알아봐요")
    button = discord.ui.Button(style=discord.ButtonStyle.primary, label="나의 외국어 mbti 확인하기", url="https://doda.app/quiz/89gxdaXnTI")
    view = discord.ui.View()
    view.add_item(button)
    await ctx.send(embed=embed, view=view)
    
#------------------------------------------------#
@bot.command(name="역할")
async def show_roles(ctx):
    roles = ctx.author.roles[1:]  # Exclude the everyone role
    embed = discord.Embed(title=f"{ctx.author.name}님의 역할입니다", color=0x00ff00)
    
    # Add each role and its icon to the embed's description
    for role in roles:
        embed.description = f"{embed.description}\n{role.name}"
        if role.icon:
            embed.set_thumbnail(url=role.icon.url)
            
    await ctx.send(embed=embed)

#------------------------------------------------검색------------------------------------------------------#

@bot.command(name='검색')
async def search(ctx, *args):
  query = ' '.join(args)
  search_url = f'https://openapi.naver.com/v1/search/webkr.json?query={query}'

  headers = {
    'X-Naver-Client-Id': 'iuWr9aAAyKxNnRsRSQIt' ,
    'X-Naver-Client-Secret': 'bkfPugeyIa'
  }
  response = requests.get(search_url, headers=headers)

  if response.status_code == 200:
    data = response.json()

    if len(data['items']) > 0:
      # Extract the top 3 search results
      results = data['items'][:3]

      # Format the results as an embedded message
      embed = discord.Embed(title=f"Search Results for \"{query}\"", color=0x0099ff)

      for result in results:
        embed.add_field(name=result['title'], value=result['link'], inline=False)

      await ctx.send(embed=embed)
    else:
      await ctx.send(f"검색결과가 없습니다 \"{query}\".")
  else:
    await ctx.send('에러가 발생했어요! 명령어를 깜빡 하신건 아닐까요?')
    
@bot.command(name='이미지')
async def search_image(ctx, *args):
    query = ' '.join(args)
    search_url = f'https://openapi.naver.com/v1/search/image?query={query}'

    headers = {
    'X-Naver-Client-Id': 'iuWr9aAAyKxNnRsRSQIt' ,
    'X-Naver-Client-Secret': 'bkfPugeyIa'
    }

    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if len(data['items']) > 0:
            # Extract the top 2 search results
            results = data['items'][:2]

            # Create a separate embedded message for each search result
            for result in results:
                embed = discord.Embed(color=0x0099ff)
                embed.set_image(url=result['thumbnail'])
                await ctx.send(embed=embed)
        else:
            await ctx.send(f"No search results for \"{query}\".")
    else:
        await ctx.send('에러가 요발생했어요')

#------------------------------------------------로또------------------------------------------------------#

@bot.command(name='로또')
async def lotto(ctx):
    Text = ""
    number = [1, 2, 3, 4, 5, 6] # 배열크기 선언해줌
    count = 0
    for i in range(0, 6):
        num = random.randrange(1, 46)
        number[i] = num
        if count >= 1:
            for i2 in range(0, i):
                if number[i] == number[i2]:  # 만약 현재랜덤값이 이전숫자들과 값이 같다면
                    numberText = number[i]
                    print("작동 이전값 : " + str(numberText))
                    number[i] = random.randrange(1, 46)
                    numberText = number[i]
                    print("작동 현재값 : " + str(numberText))
                    if number[i] == number[i2]:  # 만약 다시 생성한 랜덤값이 이전숫자들과 또 같다면
                        numberText = number[i]
                        print("작동 이전값 : " + str(numberText))
                        number[i] = random.randrange(1, 46)
                        numberText = number[i]
                        print("작동 현재값 : " + str(numberText))
                        if number[i] == number[i2]:  # 만약 다시 생성한 랜덤값이 이전숫자들과 또 같다면
                            numberText = number[i]
                            print("작동 이전값 : " + str(numberText))
                            number[i] = random.randrange(1, 46)
                            numberText = number[i]
                            print("작동 현재값 : " + str(numberText))

        count = count + 1
        Text = Text + "  " + str(number[i])

    print(Text.strip())
    embed = discord.Embed(
        title="망령의 추천 번호는!",
        description=Text.strip(),
        colour=discord.Color.red()
    )
    await ctx.send(embed=embed)
        
#------------------------------------------------검색------------------------------------------------------# 

@bot.command(name='주사위')
async def dice(ctx):
    randomNum = random.randrange(1, 7) # 1~6까지 랜덤수
    print(randomNum)
    if randomNum == 1:
        await ctx.send(embed=discord.Embed(description=':game_die: '+ ':one:'))
    if randomNum == 2:
        await ctx.send(embed=discord.Embed(description=':game_die: ' + ':two:'))
    if randomNum ==3:
        await ctx.send(embed=discord.Embed(description=':game_die: ' + ':three:'))
    if randomNum ==4:
        await ctx.send(embed=discord.Embed(description=':game_die: ' + ':four:'))
    if randomNum ==5:
        await ctx.send(embed=discord.Embed(description=':game_die: ' + ':five:'))
    if randomNum ==6:
        await ctx.send(embed=discord.Embed(description=':game_die: ' + ':six: '))
#Run the bot
bot.run(TOKEN)
