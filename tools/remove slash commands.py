import discord
from discord import app_commands
from discord.ext import commands

TOKEN = '' #bot token
application_id =  #bot application id

intents = discord.Intents.none()

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents, id=application_id,help_command=None)

@bot.event
async def on_ready():
    await bot.tree.sync()
    exit()

bot.run(TOKEN)