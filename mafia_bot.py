import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix = ';')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("게임을 준비"))
    print('Bot is ready.')

@client.command()
async def reload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
    finally:
        client.load_extension(f'cogs.{extension}')

for filename in os.listdir('.\\cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

f = open("D://dev/discord_bot/mafia_bot/token.txt", 'r')
token = f.readline()
client.run(token)
f.close()