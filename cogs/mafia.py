import discord
from discord.ext import commands
import math
import random
import time
import asyncio
import os

class Mafia(commands.Cog):
    d = {}
    x = {}
    v = {}
    voted = []

    player_name = []

    agree = 0
    disagree = 0

    survivor = 0
    mafia_num = 0
    innocent_num = 0
    doc_num = 0
    pol_num = 0
    
    deadman = False
    end = False
    healman = False
    vote_time = False
    searchman = False
    search_index = True

    status = ['밤이 되었습니다.', '낮이 되었습니다.', '지목투표 시간입니다.', '최종변론 시간입니다.', '찬반투표 시간입니다.', '해가 지기 시작합니다.']

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('mafia is ready.')

    # Commands
    @commands.command(aliases=['마피아'])
    async def main(self, ctx):
        self.d = {}
        self.x = {}
        self.v = {}
        self.voted = []

        self.player_name = []

        self.agree = 0
        self.disagree = 0

        self.survivor = 0
        self.mafia_num = 0
        self.innocent_num = 0
        self.doc_num = 0
        self.pol_num = 0

        self.deadman = False
        self.end = False
        self.healman = False
        self.vote_time = False

        #인원 체크할 채널 : 보충 필요 
        voice_channel = discord.utils.get(ctx.message.guild.channels, name="💡작업실(아침 11시~)", type=discord.ChannelType.voice)

        #채널 내 멤버 체크
        in_channel = voice_channel.members

        #인원 이름, 수 체크
        for player in in_channel:
            if player.bot:
                continue
            self.player_name.append(player.name)
            self.survivor += 1

        #직업 인원 선정
        if self.survivor <= 4:
            self.mafia_num = 1
            self.innocent_num = self.survivor - self.mafia_num
        elif self.survivor == 5:
            self.mafia_num = 1
            self.doc_num = 1
            self.innocent_num = self.survivor - self.mafia_num - self.doc_num
        else:
            self.mafia_num = int(math.sqrt(self.survivor))
            self.doc_num = 1
            self.pol_num = 1
            self.innocent_num = self.survivor - self.mafia_num - self.doc_num - self.pol_num
        
        #직업 리스트
        class_list = ['시민' for i in range(self.innocent_num)]
        for _ in range(self.mafia_num):
            class_list.append('마피아')
        for _ in range(self.doc_num):
            class_list.append('의사')
        for _ in range(self.pol_num):
            class_list.append('경찰')
        random.shuffle(class_list)
        print(class_list)
        
        self.innocent_num = self.survivor - self.mafia_num

        #직업 알리기
        i = 0
        for player in in_channel:
            if player.bot:
                continue
            channel = await player.create_dm()
            embed = discord.Embed(title='당신의 직업: {}'.format(class_list[i]), description="")
            
            if class_list[i] == '마피아':
                file = discord.File('D:\\dev\\discord_bot\\mafia_bot\\images\\mafia.png', filename='mafia.png')
                embed.set_footer(text=";목록으로 생존자 목록을 불러옵니다.\n;암살 [이름]으로 암살할 생존자를 선택합니다.")
            elif class_list[i] == '시민':
                file = discord.File('D:\\dev\\discord_bot\\mafia_bot\\images\\innocent.png', filename='innocent.png')
                embed.set_footer(text="모든 마피아를 찾아내야 합니다.")
            elif class_list[i] == '의사':
                file = discord.File('D:\\dev\\discord_bot\\mafia_bot\\images\\innocent.png', filename='innocent.png')
                embed.set_footer(text=";목록으로 생존자 목록을 불러옵니다.\n;치료 [이름]으로 살려낼 생존자를 선택합니다.")
            elif class_list[i] == '경찰':
                file = discord.File('D:\\dev\\discord_bot\\mafia_bot\\images\\innocent.png', filename='innocent.png')
                embed.set_footer(text=";목록으로 생존자 목록을 불러옵니다.\n;조사 [이름]으로 조사할 생존자를 선택합니다.")
            await channel.send(file=file, embed=embed)
            self.d[player.name] = class_list[i]
            self.x[player.name] = class_list[i]
            i += 1
        print(self.d)

        #게임시작 알림
        embed = discord.Embed(title='게임이 시작되었습니다.', description=f"총 인원 : {self.survivor}\n마피아 : {self.mafia_num}\n의사 : {self.doc_num}\n경찰 : {self.pol_num}\n시민 : {self.innocent_num}")
        file_name = random.choice(os.listdir("D:\\image\\japan"))
        file = discord.File('D:\\image\\japan\\{}'.format(file_name), filename=file_name)
        await ctx.send(file=file, embed=embed)
        await asyncio.sleep(7)

        #타임라인 시작
        await self.cycle(ctx, 0)

        if self.end:
            for job in self.x:
                await ctx.send(f'{job} : {self.x[job]}')
            return
            
        

    @commands.command(aliases=['목록'])
    async def survivor_list(self, ctx):
        embed = discord.Embed(title='생존자 목록', description="")
        embed.set_footer(text='특수능력을 사용하기 위해서는 정확한 이름을 입력해야 합니다.')
        for survivor in self.player_name:
            if survivor in self.d:
                if self.d[survivor] == '마피아' and self.d[ctx.author.name] == '마피아':
                    embed.add_field(name =f'{survivor}', value = '마피아',inline=False)
                else:
                    embed.add_field(name =f'{survivor}', value = '시민',inline=False)
            else:
                embed.add_field(name =f'{survivor}', value = '사망',inline=False)
        await ctx.author.send(embed=embed)

    ###### 이모티콘 투표 기능 추가++++++++++++++++++++++
    @commands.command(aliases=['투표'])
    async def vote1(self, ctx, *, name):
        if self.vote_time:
            if not ctx.author.name in self.voted:
                if name in self.v:
                    self.v[name] += 1
                    self.voted.append(ctx.author.name)
                    await ctx.send('투표 하셨습니다.')
                elif name in self.d:
                    self.v[name] = 1
                    self.voted.append(ctx.author.name)
                    await ctx.send('투표 하셨습니다.')
            else:
                await ctx.send('이미 투표하였습니다.')
        else:
            await ctx.send('투표 시간이 아닙니다.')
        print(self.v)

    @commands.command()
    async def last(self, ctx):
        print(self.v)
        x = max(self.v)
        await ctx.send(f'{x}님이 마피아로 지목되었습니다.')
        await asyncio.sleep(5)
        await ctx.send(f'{x}님의 최종변론 시간입니다.')
        self.voted = []
        
    @commands.command('찬성')
    async def yes(self, ctx):
        if self.vote_time:
            if ctx.author.name in self.voted:
                await ctx.send('이미 투표하였습니다.')
            else:
                self.agree += 1
                self.voted.append(ctx.author.name)
                await ctx.send('투표 하셨습니다.')
        else:
            await ctx.send('투표 시간이 아닙니다.')

    @commands.command('반대')
    async def no(self, ctx):
        if self.vote_time:
            if ctx.author.name in self.voted:
                await ctx.send('이미 투표하였습니다.')
            else:
                self.disagree += 1
                self.voted.append(ctx.author.name)
                await ctx.send('투표 하셨습니다.')
        else:
            await ctx.send('투표 시간이 아닙니다.')

    @commands.command()
    async def vote2_result(self, ctx):
        if self.agree > self.disagree:
            if self.d[max(self.v)] == '마피아':
                self.mafia_num -= 1
            else:
                self.innocent_num -= 1

            del self.d[max(self.v)]
            self.deadman = max(self.v)
            await ctx.send(f'{self.deadman}님이 죽었습니다.')
            await asyncio.sleep(10)
            self.deadman = False
            self.voted = []
        else:
            await ctx.send('가까스로 사형을 피했습니다.')
            await asyncio.sleep(10)
    
    #지목 한번만@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #번호로 지목할 수 있게@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @commands.command(aliases=['암살'])
    async def kill(self, ctx, *, person):
        if self.d[ctx.author.name] == '마피아':
            if person in self.d:
                await ctx.author.send('능력을 사용할 생존자 : [{}]'.format(person))
                if self.d[person] == '마피아':
                    while True:
                        await ctx.author.send('내가 시발 마피아 죽이지 말라 했지?')
                self.deadman = person
            else:
                await ctx.author.send('정확한 이름을 입력해주세요.')
        else:
            await ctx.author.send('당신은 마피아가 아닙니다.')

    @commands.command(aliases=['조사'])
    async def search(self, ctx, *, person):
        if self.search_index:
            if self.d[ctx.author.name] == '경찰':
                if person in self.d:
                    await ctx.author.send('능력을 사용할 생존자 : [{}]'.format(person))
                    if self.d[person] == '마피아':
                        await ctx.author.send('그는 마피아가 맞습니다.')
                    else:
                        await ctx.author.send('마피아가 아닌듯 합니다.')
                    self.search_index = False
                else:
                    await ctx.author.send('정확한 이름을 입력해주세요.')
            else:
                await ctx.author.send('당신은 경찰이 아닙니다.')
        else:
            await ctx.author.send('이미 조사하였습니다.')

    @commands.command(aliases=['치료'])
    async def heal(self, ctx, *, person):
        if self.d[ctx.author.name] == '의사':
            if person in self.d:
                await ctx.author.send('능력을 사용할 생존자 : [{}]'.format(person))
                self.healman = person
            else:
                await ctx.author.send('정확한 이름을 입력해주세요.')
        else:
            await ctx.author.send('당신은 의사가 아닙니다.')

    async def dead(self, ctx):
        #죽은사람 추방/음소거 기능 추가해야함+++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.deadman and self.deadman != self.healman:
            await ctx.send(f'{self.deadman}님이 죽었습니다.')
            del self.d[self.deadman]
            self.innocent_num -= 1
            await asyncio.sleep(5)
        elif self.deadman and self.deadman == self.healman:
            await ctx.send('누군가 마피아의 습격을 받았지만 의사의 도움으로 살아남았습니다!')
            await asyncio.sleep(5)
        else:
            await ctx.send('지난 밤에는 아무일도 일어나지 않았습니다.')
            await asyncio.sleep(5)
        self.deadman = False

    async def over(self, ctx):
        if self.mafia_num >= self.innocent_num:
            embed = discord.Embed(title='마피아의 승리입니다!', description='')
            embed.set_footer(text='도시가 마피아에게 점령되었습니다.')
            file = discord.File('D:\\dev\\discord_bot\\mafia_bot\\images\\mafia_win.jpg', filename='mafia_win.jpg')
            await ctx.send(file=file, embed=embed)
            self.end = True
        elif self.mafia_num == 0:
            await ctx.send('게임이 종료되었습니다.[시민 승]')
            embed = discord.Embed(title='시민들의 승리입니다!', description='')
            embed.set_footer(text='시민들의 힘으로 도시를 지켜내었습니다.')
            file = discord.File('D:\\dev\\discord_bot\\mafia_bot\\images\\excute.jpg', filename='excute.jpg')
            await ctx.send(file=file, embed=embed)
            self.end = True

    @commands.command()
    async def cycle(self, ctx, idx):
        #낮이 되었을 때
        embed = discord.Embed(title=f'{self.status[idx]}', description='')

        #밤
        if idx == 0:
            self.agree = 0
            self.disagree = 0
            self.healman = False
            self.deadman = False
            self.v = {}
            self.search_index = True
            embed.set_footer(text='문 밖은 쥐 죽은 듯이 조용합니다.')
            file = discord.File('D:\\dev\\discord_bot\\mafia_bot\\images\\night.png', filename='night.png')
            sec = 30
        #낮
        elif idx == 1:
            await self.dead(ctx)
            await self.over(ctx)
            if self.end:
                return
            embed.set_footer(text='사람들이 광장에 모이기 시작합니다.')
            file_name = random.choice(os.listdir("D:\\image\\japan"))
            file = discord.File('D:\\image\\japan\\{}'.format(file_name), filename=file_name)
            sec = 15 * self.survivor

        #이외
        elif idx == 2:
            self.vote_time = True
            embed.set_footer(text=';투표 [이름]으로 마피아를 지목합니다.')
            for survivor in self.player_name:
                if survivor in self.d:
                    embed.add_field(name =f'{survivor}', value = '생존',inline=True)
                else:
                    embed.add_field(name =f'{survivor}', value = '사망',inline=True)
            file_name = random.choice(os.listdir("D:\\image\\japan"))
            file = discord.File('D:\\image\\japan\\{}'.format(file_name), filename=file_name)
            sec = 20
        elif idx == 3:
            self.vote_time = False
            await self.last(ctx)
            await asyncio.sleep(5)
            embed.set_footer(text='자신이 마피아가 아닌 이유를 설명해주세요.')
            embed.add_field(name =f'{max(self.v)}님의 최다득표', value = '마피아로 지목되었습니다.',inline=True) ##
            file_name = random.choice(os.listdir("D:\\image\\japan"))
            file = discord.File('D:\\image\\japan\\{}'.format(file_name), filename=file_name)
            sec = 20
        elif idx == 4:
            self.vote_time = True
            file_name = random.choice(os.listdir("D:\\image\\japan"))
            file = discord.File('D:\\image\\japan\\{}'.format(file_name), filename=file_name)
            embed.set_footer(text=';찬성 또는 ;반대로 투표할 수 있습니다.')
            sec = 20
        elif idx == 5: 
            self.vote_time = False
            await self.vote2_result(ctx)
            await self.over(ctx)
            if self.end:
                return
            file_name = random.choice(os.listdir("D:\\image\\japan"))
            file = discord.File('D:\\image\\japan\\{}'.format(file_name), filename=file_name)
            embed.set_footer(text='다가올 밤을 준비하십시오.')
            sec = 20

        #설정된 이미지와 메시지 출력
        await ctx.send(file=file, embed=embed)
        await asyncio.sleep(3)

        #남은시간
        await ctx.send(f'{sec}초 남았습니다.')
        await asyncio.sleep(sec-15)
        await ctx.send('15초 남았습니다.')
        await asyncio.sleep(10)
        await ctx.send('5초 남았습니다.')
        await asyncio.sleep(5)

        if idx == 5:
            await self.cycle(ctx, 0)
        else:
            await self.cycle(ctx, idx+1)


def setup(client):
    client.add_cog(Mafia(client))