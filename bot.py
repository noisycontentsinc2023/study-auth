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
import gspread.exceptions
import re
import pytz

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
sheet3 = client.open('서버기록').worksheet('랜덤미션')
rows = sheet3.get_all_values()

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

#------------------------------------------------#
sheet3 = client.open('서버기록').worksheet('랜덤미션')
rows = sheet3.get_all_values()

@bot.command(name='미션인증')
async def random_mission_auth(ctx):
    username = str(ctx.message.author)
    # Check if the user has already authenticated today
    today = datetime.datetime.now().strftime('%m%d')
    try:
        user_row = sheet3.find(username).row
    except gspread.exceptions.CellNotFound:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    if sheet3.cell(user_row, sheet3.find(today).col).value == '1':
        # If the user has already authenticated today, send an error message
        embed = discord.Embed(title='', description='오늘 이미 인증하셨어요!')
        await ctx.send(embed=embed)
    else:
        # If the user has not authenticated today, send an authentication window
        embed = discord.Embed(title='Authentication', description=f'{username}\'s authentication for today. 미션 인증 대기 중')
        view = discord.ui.View()
        button = AuthButton(ctx, username, today)
        view.add_item(button)
        await ctx.send(embed=embed, view=view)
        
class AuthButton2(discord.ui.Button):
    def __init__(self, ctx, username, today):
        super().__init__(style=discord.ButtonStyle.green, label="Authenticate")
        self.ctx = ctx
        self.username = username
        self.today = today

    async def callback(self, interaction: discord.Interaction):
        if discord.utils.get(interaction.user.roles, id=922400231549722664) is None:
            # If the user doesn't have the required role, send an error message
            embed = discord.Embed(title='Error', description='You do not have permission to authenticate.')
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

        # Send a success message
        embed = discord.Embed(title='Success', description=f'{self.username} has been authenticated. 정상적으로 인증되셨습니다')
        await interaction.message.edit(embed=embed, view=None)
        
#------------------------------------------------#
# Set up Google Sheets worksheet
sheet2 = client.open('서버기록').worksheet('일취월장')
rows = sheet2.get_all_values()
class AuthButton(discord.ui.Button):
    def __init__(self, ctx, user, date):
        super().__init__(style=discord.ButtonStyle.green, label="확인 ")
        self.ctx = ctx
        self.user = user
        self.date = date
    
    async def callback(self, interaction: discord.Interaction):
        if discord.utils.get(interaction.user.roles, id=922400231549722664) is None:
            return
        existing_users = sheet2.col_values(1)
        if str(self.user) not in existing_users:
            empty_row = len(existing_users) + 1
            sheet2.update_cell(empty_row, 1, str(self.user))
            existing_dates = sheet2.row_values(1)
            if self.date not in existing_dates:
                empty_col = len(existing_dates) + 1
                sheet2.update_cell(1, empty_col, self.date)
                sheet2.update_cell(empty_row, empty_col, "1")
            else:
                col = existing_dates.index(self.date) + 1
                sheet2.update_cell(empty_row, col, "1")
        else:
            index = existing_users.index(str(self.user)) + 1
            existing_dates = sheet2.row_values(1)
            if self.date not in existing_dates:
                empty_col = len(existing_dates) + 1
                sheet2.update_cell(1, empty_col, self.date)
                sheet2.update_cell(index, empty_col, "1")
            else:
                col = existing_dates.index(self.date) + 1
                sheet2.update_cell(index, col, "1")
        await interaction.message.edit(embed=discord.Embed(title="인증상황", description=f"{interaction.user.mention}님이 {self.ctx.author.mention}의 {self.date} 일취월장 인증을 완료됐습니다"), view=None)

@bot.command(name='인증')
async def Authentication(ctx, date):
    
    # Validate the input date
    if not re.match(r'^(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])$', date):
        await ctx.send("정확한 날짜를 입력해주세요! 날짜는 네 자리 숫자로 작성해주세요. 1월 1일을 입력하시려면 0101을 입력해주세요.")
        return
      
    existing_users = sheet2.col_values(1)
    if str(ctx.author) in existing_users:
        user_index = existing_users.index(str(ctx.author)) + 1
        existing_dates = sheet2.row_values(1)
        if date in existing_dates:
            date_index = existing_dates.index(date) + 1
            cell_value = sheet2.cell(user_index, date_index).value
            if cell_value == "1":
                await ctx.send(embed=discord.Embed(title="인증상황", description=f"{ctx.author.mention}님, 해당 날짜는 이미 인증되었습니다!"))
                return

    embed = discord.Embed(title="인증상황", description=f"{ctx.author.mention}의 {date} 일취월장 인증입니다")
    view = discord.ui.View()
    button = AuthButton(ctx, ctx.author, date)
    view.add_item(button)
    msg = await ctx.send(embed=embed, view=view)

    def check(interaction: discord.Interaction):
        return interaction.message.id == msg.id and interaction.data.get("component_type") == discord.ComponentType.button.value

    await bot.wait_for("interaction", check=check)
    
#Run the bot
bot.run(TOKEN)
