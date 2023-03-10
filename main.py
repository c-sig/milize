from config import *
from commands import permissions
from commands import boards


config_file, config, bot, group_name, token, owners, managers, members, task_path = initializebot()

@bot.command(name='sync', description='Syncs the command tree (slash commmands) for the bot!')
async def sync(ctx):
    await bot.tree.sync()
    print('done')

bot.tree.add_command(permissions.permissiongroup)
bot.tree.add_command(boards.boardgroup)

bot.run(token)
