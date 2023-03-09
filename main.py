import enum
import os
import json
import discord
import configparser
from pathlib import Path
from discord import app_commands
from discord.ext import commands
from config import *
from commands import permissions


config_file, config, bot, group_name, token, owners, managers, members, task_path = initializebot()

@bot.command(name='sync', description='Syncs the command tree (slash commmands) for the bot!')
async def sync(ctx):
    await bot.tree.sync()
    print('done')

bot.tree.add_command(permissions.permissiongroup)

bot.run(token)
