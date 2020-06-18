import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time
import asyncio
import sys


class Work(commands.Cog):
    now = datetime.now()

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Work is ready.')

    @commands.command(aliases=['작업'])
    async def _help(self, ctx):
        embed = discord.Embed(title = "작업에 관한 명령어", description = "모든 명령어는 `;`로 시작합니다.")
        embed.set_footer(text="작업하자.")
        embed.add_field(name = "작업",value = "`작업시작`\n`식사`\n`작업끝`\n`남은시간`",inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['작업시작'])
    async def start(self, ctx):
        self.meal = False
        while True:
            await self.work_on(ctx)
            await ctx.send('@Skoo#1029')
            if self.meal:
                await self.meal_time
            else:
                await self.work_rest(ctx)
            await ctx.send('@Skoo#1029')

    @commands.command(aliases=['작업끝'])
    async def work_off(self, ctx):
        lnow = datetime.now()
        embed = discord.Embed(title='작업 Off', description=lnow.strftime("```현재시각 : %H시 %M분```"))
        embed.set_footer(text="수고하셨습니다.")
        await ctx.send(embed=embed)
        sys.exit()

    @commands.command(aliases=['남은시간'])
    async def time_left(self, ctx):
        lnow = datetime.now()
        embed = discord.Embed(title='남은 시간', description=(f"```{50 - (lnow - self.now).days}분 남았습니다.```"))
        embed.set_footer(text="Keep going")
        await ctx.send(embed=embed)

    @commands.command(aliases=['식사'])
    async def set_meal(self, ctx):
        self.meal = True
        embed = discord.Embed(title='식사 시간 설정됨', description="```작업 종료 후 식사 시간```")
        embed.set_footer(text="뭐먹지")
        await ctx.send(embed=embed)

    async def work_on(self, ctx):
        self.now = datetime.now()
        embed = discord.Embed(title='작업 On', description=self.now.strftime("```현재시각 : %H시 %M분```"))
        embed.set_footer(text="50분 뒤 휴식 On")
        await ctx.send(embed=embed)

        await asyncio.sleep(50*60)

    async def work_rest(self, ctx):
        self.now = datetime.now()
        embed = discord.Embed(title='휴식 On', description=self.now.strftime("```현재시각 : %H시 %M분```"))
        embed.set_footer(text="10분 뒤 작업 On")
        await ctx.send(embed=embed)
        await asyncio.sleep(10*60)

    async def meal_time(self, ctx):
        self.now = datetime.now()
        embed = discord.Embed(title='식사 On', description=self.now.strftime("```현재시각 : %H시 %M분```"))
        embed.set_footer(text="1시간 뒤 작업 On")
        await ctx.send(embed=embed)

        await asyncio.sleep(60*60)
        self.meal = False



def setup(client):
    client.add_cog(Work(client))