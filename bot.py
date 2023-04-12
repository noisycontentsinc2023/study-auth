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
import gspread

from google.oauth2 import service_account
from discord import Embed
from discord.ext import tasks, commands
from discord.ext.commands import Context
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
# Set up Google Sheets worksheet
sheet3 = client.open('서버기록').worksheet('랜덤미션')
rows = sheet3.get_all_values()

kst = pytz.timezone('Asia/Seoul')
now = datetime.datetime.now(kst)

@bot.command(name='등록')
async def Register(ctx):
    username = str(ctx.message.author)
    
    # Find the first empty row in column A
    row = 2
    while sheet3.cell(row, 1).value:
        row += 1

    # Append the username to the first empty row in column A
    sheet3.update_cell(row, 1, username)

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


@bot.command(name='미션')
async def Random_Mission(ctx):
    # Check if the user has the required role
    required_role = discord.utils.get(ctx.guild.roles, id=1093781563508015105)
    if required_role in ctx.author.roles:
        if str(ctx.channel.id) == "1093780375890825246":
            await lottery(ctx)
        else:
            await ctx.send("이 채널에서는 사용할 수 없는 명령입니다")
    else:
        # Send the message if the user does not have the required role
        embed = discord.Embed(description="랜덤미션스터디 참여자만 !미션 명령어를 사용할 수 있어요", color=0xff0000)
        await ctx.send(embed=embed)


async def lottery(ctx):
    choices = [('Mission 1', '★'), ('Mission 2', '★★'),
               ('Mission 3', '★★★'),
               ('Mission 4', '★★'), ('Mission Pass!', '★'), ('Mission 6', '★★'), ('Mission 7', '★★★'), ('Mission 8', '★★'),
               ('Mission 9', '★★★'), ('Mission 10', '★★')]

    embed = discord.Embed(title=f"{ctx.author.name}님의 오늘의 미션입니다!", color=0xff0000)
    message = await ctx.send(embed=embed)
    message_id = message.id
    selected_choices = random.sample(choices, 10)

    for i, (choice, difficulty) in enumerate(selected_choices):
        embed.clear_fields()
        embed.add_field(name=f'{i + 1} 미션', value=choice, inline=True)
        embed.add_field(name='난이도', value=difficulty, inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(0.2)

    result, difficulty = random.choice(selected_choices)
    embed.clear_fields()
    embed.add_field(name='난이도', value=difficulty, inline=False)
    embed.set_footer(text='오늘의 미션입니다!')
    view = RandomMissionView(ctx, message)
    await message.edit(embed=embed, view=view)

@bot.command(name='再次')
async def Relottery(ctx):
    choices = [('Mission 1', '★'), ('Mission 2', '★★'),
               ('Mission 3', '★★★'),
               ('Mission 4', '★★'), ('Mission Pass!', '★'), ('Mission 6', '★★'), ('Mission 7', '★★★'), ('Mission 8', '★★'),
               ('Mission 9', '★★★'), ('Mission 10', '★★')]

    embed = discord.Embed(title=f"{ctx.author.name}님의 다시 뽑기 결과입니다!", color=0xff0000)
    message = await ctx.send(embed=embed)
    message_id = message.id
    selected_choices = random.sample(choices, 10)

    for i, (choice, difficulty) in enumerate(selected_choices):
        embed.clear_fields()
        embed.add_field(name=f'{i + 1} 미션', value=choice, inline=True)
        embed.add_field(name='난이도', value=difficulty, inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(0.2)

    result, difficulty = random.choice(selected_choices)
    embed.clear_fields()
    embed.add_field(name='난이도', value=difficulty, inline=False)
    embed.set_footer(text='오늘의 미션입니다!')
    await message.edit(embed=embed, view=view)

@bot.command(name='미션인증')
async def random_mission_auth(ctx):
    username = str(ctx.message.author)
    # Check if the user has already authenticated today
    today = now.strftime('%m%d')
    
    user_row = None
    for row in sheet3.get_all_values():
        if username in row:
            user_row = row
            break

    if user_row is None:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    user_cell = sheet3.find(username)
    if sheet3.cell(user_cell.row, sheet3.find(today).col).value == '1':
        # If the user has already authenticated today, send an error message
        embed = discord.Embed(title='', description='오늘 이미 인증하셨어요!')
        await ctx.send(embed=embed)
    else:
        # If the user has not authenticated today, send an authentication window
        embed = discord.Embed(title='Authentication', description=f'{username}님의 미션 인증 대기 중')
        view = discord.ui.View()
        button = AuthButton2(ctx, username, today)
        view.add_item(button)
        message = await ctx.send(embed=embed, view=view)

        # Start a background task to refresh the button every minute
        asyncio.create_task(refresh_button(ctx, message, button, username, today))
        
async def refresh_button(ctx, message, button, username, today):
    auth_event = button.auth_event

    while not auth_event.is_set():
        # Wait for 1 minute
        await asyncio.sleep(60)

        # If the button was not clicked, refresh it
        if not auth_event.is_set():
            view = discord.ui.View()
            new_button = AuthButton2(ctx, username, today)
            view.add_item(new_button)
            await message.edit(view=view)
            
class AuthButton2(discord.ui.Button):
    def __init__(self, ctx, username, today):
        super().__init__(style=discord.ButtonStyle.green, label="인증대기")
        self.ctx = ctx
        self.username = username
        self.today = today
        self.auth_event = asyncio.Event()

    async def callback(self, interaction: discord.Interaction):
        if discord.utils.get(interaction.user.roles, id=922400231549722664) is None:
            # If the user doesn't have the required role, send an error message
            embed = discord.Embed(title='Error', description='권한이 없습니다 :(')
            await interaction.message.edit(embed=embed, view=None)
            return

        try:
            user_row = sheet3.find(self.username).row
        except gspread.exceptions.CellNotFound:
            embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
            await interaction.message.edit(embed=embed, view=None)
            return

        # Authenticate the user in the spreadsheet
        today_col = sheet3.find(self.today).col
        sheet3.update_cell(user_row, today_col, '1')
        
        # Set the auth_event to stop the loop
        self.auth_event.set()
        
        # Remove the button from the view
        self.view.clear_items()
        
        # Send a success message
        embed = discord.Embed(title='인증완료!', description=f'{self.username}님, 정상적으로 인증되셨습니다')
        await interaction.message.edit(embed=embed, view=None)
        
@bot.command(name='누적')
async def mission_count(ctx):
    username = str(ctx.message.author)
    
    # Find the user's row in the Google Sheet
    user_row = None
    for row in sheet3.get_all_values():
        if username in row:
            user_row = row
            break

    if user_row is None:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    user_cell = sheet3.find(username)
    count = int(sheet3.cell(user_cell.row, 9).value)  # Column I is the 9th column

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
@bot.command(name="역할")
async def show_roles(ctx):
    roles = [role.name for role in ctx.author.roles]
    embed = discord.Embed(title=f"{ctx.author.name}님의 역할", description=", ".join(roles), color=0x00ff00)
    await ctx.send(embed=embed)
    
#------------------------------------------------#    
class ChannelSelect(discord.ui.Select):
    def __init__(self, ctx, options):
        super().__init__(placeholder='채널 선택', options=options)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        selected_channel = self.ctx.guild.get_channel(int(self.values[0]))
        await self.ctx.send(f'{selected_channel.mention} 채널이 선택되었습니다.')

@bot.command(name='채널')
async def select_channel(ctx):
    # 유저가 접근 가능한 카테고리 찾기
    accessible_categories = []
    for category in ctx.guild.categories:
        if ctx.author in category.members and len(category.channels) > 0:
            accessible_categories.append(category)

    if not accessible_categories:
        await ctx.send('접근 가능한 카테고리가 없습니다.')
        return

    # 셀렉트 메뉴에 보여줄 옵션 생성하기
    options = []
    for category in accessible_categories:
        option = discord.SelectOption(label=category.name, value=str(category.id))
        options.append(option)

    # 옵션을 포함한 ChannelSelect 클래스 생성하기
    select_category = ChannelSelect(ctx, options=options)

    # ChannelSelect 클래스를 포함한 discord.ui.View 객체 생성하기
    category_view = discord.ui.View()
    category_view.add_item(select_category)
    category_message = await ctx.send('어떤 카테고리를 선택하시겠습니까?', view=category_view)

    # 카테고리 선택을 기다린 후 선택된 카테고리의 채널을 보여주기
    try:
        interaction = await bot.wait_for('select_option', check=lambda i: i.user.id == ctx.author.id and i.message.id == category_message.id, timeout=30)
        selected_category = ctx.guild.get_channel(int(interaction.values[0]))

        channel_options = []
        for channel in selected_category.channels:
            if channel.permissions_for(ctx.author).read_messages:
                option = discord.SelectOption(label=channel.name, value=str(channel.id))
                channel_options.append(option)

        if not channel_options:
            await ctx.send('해당 카테고리에 접근 가능한 채널이 없습니다.')
            return

        select_channel = ChannelSelect(ctx, options=channel_options)
        channel_view = discord.ui.View()
        channel_view.add_item(select_channel)
        channel_message = await ctx.send('어떤 채널을 선택하시겠습니까?', view=channel_view)

        interaction = await bot.wait_for('select_option', check=lambda i: i.user.id == ctx.author.id and i.message.id == channel_message.id, timeout=30)
        selected_channel = ctx.guild.get_channel(int(interaction.values[0]))
        await ctx.send(f'{selected_channel.mention} 채널이 선택되었습니다.')
        
    except asyncio.TimeoutError:
        await message.edit(content='시간이 초과되었습니다.', view=None)
        return
        
#Run the bot
bot.run(TOKEN)
