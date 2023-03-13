from config import *
from commands import permissions
from commands import boards
from commands import tasks
from commands import jobs


prefix, config_file, config, bot, group_name, token, owners, managers, members = initializebot()

@bot.command(name='sync', description='Syncs the command tree (slash commmands) for the bot!')
async def sync(ctx):
    await bot.tree.sync()
    print('done')

bot.tree.add_command(jobs.jobgroup)
bot.tree.add_command(tasks.taskgroup)
bot.tree.add_command(permissions.permissiongroup)
bot.tree.add_command(boards.boardgroup)

bot.run(token)

print(jobtypes)
