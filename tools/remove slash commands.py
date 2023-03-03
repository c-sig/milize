import discord
from discord import app_commands
from discord.ext import commands

TOKEN = 'MTA3OTYzNjc5NDc1MDAxMzQ2MA.GYjKHw.65Vi2GfjEpZly7yIxS-dnyEI9f8Q8co6Q5dyww' #bot token
application_id = 1079636794750013460 #bot application id

intents = discord.Intents.none()

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents, id=application_id,help_command=None)

@bot.event
async def on_ready():
    await bot.tree.sync()
    exit()

bot.run(TOKEN)