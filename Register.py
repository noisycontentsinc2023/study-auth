import discord
from discord.ext import commands

class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @bot.command(name='등록')
    async def Register(ctx):
        username = str(ctx.message.author)
    
        sheet3, rows = await get_sheet3()

        row = 2
        while (await sheet3.cell(row, 1)).value:
            row += 1

        await sheet3.update_cell(row, 1, username)

        role = discord.utils.get(ctx.guild.roles, id=1093781563508015105)
        await ctx.author.add_roles(role)

        embed = discord.Embed(description=f"{ctx.author.mention}님, 랜덤미션스터디에 정상적으로 등록됐습니다!", color=0x00FF00)
        await ctx.send(embed=embed)
    
def setup(bot):
    bot.add_cog(Register(bot))
