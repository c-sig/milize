from config import *
from commands import permissions
from commands import boards
from commands import tasks
from commands import jobs
import os
import sys

prefix, config_file, config, bot, group_name, token, owners, managers, members = initializebot()

owner = 0  # put your discord id here for restart to work properly

@bot.command(name='sync', description='Syncs the command tree (slash commmands) for the bot!')
async def sync(ctx):
    await bot.tree.sync()
    print('done')


@bot.command(name='restart', description='Restarts the bot')
async def restart(ctx):
    if ctx.author.id == owner:
        await ctx.send("Restarting bot...")
        os.execv(sys.executable, ['python'] + sys.argv)


bot.tree.add_command(jobs.jobgroup)
bot.tree.add_command(tasks.taskgroup)
bot.tree.add_command(permissions.permissiongroup)
bot.tree.add_command(boards.boardgroup)

bot.run(token)
