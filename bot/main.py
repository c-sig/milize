# imports
import discord
from discord import app_commands
from discord.ext import commands
import json, os, traceback

# messages
print('DISCLAIMER: This bot is intended for per-group usage. In your bot settings, please set "Public Bot" to False so nobody can invite your bot!\n')

# do not change
intents = discord.Intents.all()
if not os.path.exists("configs/"):
    os.mkdir("configs")
    print('The CONFIGS folder was just created! Input your user ID into the botowners.txt file and restart the bot!')

# settings
prefix = '!' # prefix for that one text command called SYNC
sg = '' #input scanlation group name here
TOKEN = '' #bot token
application_id =  #bot application id

# init bot
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), intents=intents, id=application_id,help_command=None)

# basic functions
def save_tasks(tasks):
    with open('configs/tasks.json', 'w') as f:
        json.dump(tasks, f, indent=4)

def load_tasks():
    if os.path.exists('configs/tasks.json'):
        with open('configs/tasks.json', 'r') as f:
            return json.load(f)
    else:
        return {}
    
#setup
def read_file(filename, default=[]):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return [int(line.strip()) for line in file]
    else:
        with open(filename, "x") as file:
            pass
        return default

botowners = read_file('configs/botowners.txt')
scanowners = read_file('configs/scanowners.txt')
scanmembers = read_file('configs/scanmembers.txt')

# groups
groupgroup = app_commands.Group(name='group', description='Group commands.')
taskgroup = app_commands.Group(name='task', description='Task manipulation commands.')

# COMMANDS

@groupgroup.command(name='addscanowner',description='Gives a user scan owner permissions')
async def add_scan_owners(interaction:discord.Interaction, user:discord.Member):
    def add_to_scan_owners(member: discord.Member):
        user_id = member.id  # get the user ID from the Member object
        with open("configs/scanowners.txt", "a+") as file:
            a = file.readlines()
            for i, line in enumerate(a):
                if line.strip() == '':
                    del a[i]
            a.append(str(user_id) + '\n')
            file.writelines(a)
            file.close()
    if interaction.user.id in botowners and not user.id in scanowners:
        add_to_scan_owners(user)
        await interaction.response.send_message(f'Added {user.mention} as an owner of **{sg}**!')
    elif interaction.user.id in botowners:
        await interaction.response.send_message(f'That user is already a owner of **{sg}**!')
    else:
        embed = discord.Embed(
            title='403 Forbidden',
            color=discord.Color.red(),
            description='You do not have permissions to add users to this group!'
        )
        return await interaction.response.send_message(embed=embed)

@groupgroup.command(name='addscanmember',description='Gives a user scan member permissions')
async def add_scan_members(interaction:discord.Interaction, user:discord.Member):
    def add_to_scan_members(member: discord.Member):
        user_id = member.id  # get the user ID from the Member object
        with open("configs/scanmembers.txt", 'a+') as file:
            a = file.readlines()
            for i, line in enumerate(a):
                if line.strip() == '':
                    del a[i]
            a.append(str(user_id) + '\n')
            file.writelines(a)
            file.close()
    if interaction.user.id in botowners or interaction.user.id in scanowners and not user.id in scanmembers:
        add_to_scan_members(user)
        await interaction.response.send_message(f'Added {user.mention} as a member of **{sg}**!')
    elif interaction.user.id in botowners or interaction.user.id in scanowners:
        await interaction.response.send_message(f'That user is already a member of **{sg}**!')
    else:
        embed = discord.Embed(
            title='403 Forbidden',
            color=discord.Color.red(),
            description='You do not have permissions to add users as a group member!'
        )
        return await interaction.response.send_message(embed=embed)

@groupgroup.command(name='removescanowners', description='Remove user from scan owners')
async def remove_scan_owners(interaction:discord.Interaction, user:discord.Member):
    def remove_scan_owner(user:discord.member):
        id = user.id
        with open("configs/scanowners.txt", "r") as file:
            lines=file.readlines()
            file.close()
        lines = [line.strip() for line in lines if line.strip() != str(id)]
        with open("configs/scanowners.txt", "w") as file:
            file.write("\n".join(lines))
            file.close()
    if interaction.user.id in botowners and user.id in scanowners:
        remove_scan_owner(user)
        await interaction.response.send_message(f"Removed {user.mention} as a owner of **{sg}**!")
    elif interaction.user.id in botowners:
        await interaction.response.send_message(f"That user isn't a owner of **{sg}**!")
    else: 
        embed = discord.Embed(
            title='403 Forbidden',
            color=discord.Color.red(),
            description='You do not have permissions to remove users as scan group owners!'
        )
        return await interaction.response.send_message(embed=embed)

@groupgroup.command(name='removescanmembers', description='Remove user from scan members')
async def remove_scan_members(interaction:discord.Interaction, user:discord.Member):
    def remove_scan_member(user:discord.member):
        id = user.id
        with open("configs/scanmembers.txt", "r") as file:
            lines=file.readlines()
            file.close()
        lines = [line.strip() for line in lines if line.strip() != str(id)]
        with open("configs/scanmembers.txt", "w") as file:
            file.write("\n".join(lines))
            file.close()
    if interaction.user.id in botowners or interaction.user.id in scanowners and user.id in scanmembers:
        remove_scan_member(user)
        await interaction.response.send_message(f'Removed {user.mention} as a member of **{sg}**!')
    elif interaction.user.id in botowners or interaction.user.id in scanowners:
        await interaction.response.send_message(f"That user isn't a member of **{sg}**!")
    else: 
        embed = discord.Embed(
            title='403 Forbidden',
            color=discord.Color.red(),
            description='You do not have permissions to remove scan group members!'
        )
        return await interaction.response.send_message(embed=embed)

@groupgroup.command(name='listbotowners', description='Lists bot owners.')
async def show_users(interaction:discord.Interaction):
    with open("configs/botowners.txt", "r") as file:
        lines = file.readlines()
        file.close()
    users = []
    for line in lines:
        user_id = int(line.strip())
        member = discord.utils.get(interaction.guild.members, id=user_id)
        if member:
            users.append(f'{member.name}#{member.discriminator}')
    if users:
        users_list = '\n'.join(users)
        await interaction.response.send_message(f'**Bot owners:**\n{users_list}')
    else:
        embed = discord.Embed(
            title='404 Not Found',
            color=discord.Color.yellow(),
            description='No users are in the Bot Owners group.'
        )
        await interaction.response.send_message(embed=embed)

@groupgroup.command(name='listscanowners', description='Lists scan owners.')
async def show_users(interaction:discord.Interaction):
    with open("configs/scanowners.txt", "r") as file:
        lines = file.readlines()
        file.close()
    users = []
    for line in lines:
        user_id = int(line.strip())
        member = discord.utils.get(interaction.guild.members, id=user_id)
        if member:
            users.append(f"{member.name}#{member.discriminator}")
    if users:
        users_list = "\n".join(users)
        await interaction.response.send_message(f"Scan owners:\n{users_list}")
    else:
        embed = discord.Embed(
            title='404 Not Found',
            color=discord.Color.yellow(),
            description=f'No users are part of {sg} as owners.'
        )
        await interaction.response.send_message(embed=embed)

@groupgroup.command(name='listscanmembers', description='Lists scan group members.')
async def show_users(interaction:discord.Interaction):
    with open("configs/scanmembers.txt", "r") as file:
        lines = file.readlines()
        file.close()

    users = []
    for line in lines:
        user_id = int(line.strip())
        member = discord.utils.get(interaction.guild.members, id=user_id)
        if member:
            users.append(f"{member.name}#{member.discriminator}")
    
    if users:
        users_list = "\n".join(users)
        await interaction.response.send_message(f"Scan members:\n{users_list}")
    else:
        embed = discord.Embed(
            title='404 Not Found',
            color=discord.Color.yellow(),
            description=f'No users are part of {sg} as members.'
        )
        await interaction.response.send_message(embed=embed)

@taskgroup.command(name='assign', description='Assigns a task to someone.')
async def assign_task(interaction: discord.Interaction, board: str, task: str, user: discord.Member, job: str):
    role = job
    if interaction.user.id not in scanmembers:
        return await interaction.response.send_message('You are not part of the scanlation group and cannot use this command!')
    if user.id not in scanmembers and user.id not in scanowners:  
        return await interaction.response.send_message('That user isn\'t part of the scanlation group! Add them to the scanlation group first!')
    tasks = load_tasks()
    if board not in tasks:
        return await interaction.response.send_message(f'`That board does not exist. Use /createboard "Board" to create a board!`')
    for i, rtask in enumerate(tasks[board]):
        if rtask['task'] == task:
            et = rtask
            if any(assigned[0] == user.id and assigned[1].lower() == role.lower() for assigned in et['assigned']):
                return await interaction.response.send_message(f'`That user has already been assigned to do {role}` on {task}!')
            et['assigned'].append([user.id, role])
            tasks[board][i] = et
            save_tasks(tasks)
            return await interaction.response.send_message(f'User {user.mention} has been assigned to do `{role}` on the task `{task}` on the board `{board}`.')
    return await interaction.response.send_message(f'`That task does not exist on the board "{board}". To view the list of tasks, check /list "{board}".`')
@assign_task.autocomplete('board')
async def boardautoassigntask(interaction: discord.Interaction, current: str):
    tasks = load_tasks()
    boards = [board for board in tasks if board not in (t['status'] for t in tasks[board])]
    all_choices = [app_commands.Choice(name=name, value=name) for name in boards]
    if not current:
        return all_choices
    return [ch for ch in all_choices if ch.name.lower().startswith(current.lower())] or all_choices

@taskgroup.command(name='unassign', description='Unassign a task from someone.')
async def unassign_task(interaction:discord.Interaction, board:str, task:str, user:discord.Member, job:str):
    role = job.lower()
    if interaction.user.id in scanmembers and not interaction.user.id in scanowners:
        return await interaction.response.send_message('You do not have permission to unassign a task from someone!')
    elif not interaction.user.id in scanmembers:
        return await interaction.response.send_message('You are not part of the scanlation group and cannot use this command!')
    tasks = load_tasks()
    if board not in tasks:
        return await interaction.response.send_message(f'`That board does not exist. Use /createboard "Board" to create a board!`')
    for rtask in tasks[board]:
        if rtask['task'] == task:
            assigned = rtask['assigned']
            for i, (assigned_user_id, assigned_role) in enumerate(assigned):
                if assigned_user_id == user.id and assigned_role.lower() == role:
                    del assigned[i]
                    save_tasks(tasks)
                    return await interaction.response.send_message(f'User {user.mention} has been unassigned from the job `{job}` on the task `{task}` on the board `{board}`.')
            return await interaction.response.send_message(f'That user does not have the `{job}` job on the specified `{task}` task! Run `/list "{board}"` to see all tasks and assigned users!')
    return await interaction.response.send_message(f'`That task does not exist on the board "{board}". To view the list of tasks, check /list "{board}".`')
@unassign_task.autocomplete('board')
async def boardautoassigntask(interaction: discord.Interaction, current: str):
    tasks = load_tasks()
    boards = [board for board in tasks if board not in (t['status'] for t in tasks[board])]
    all_choices = [app_commands.Choice(name=name, value=name) for name in boards]
    if not current:
        return all_choices
    return [ch for ch in all_choices if ch.name.lower().startswith(current.lower())] or all_choices

@taskgroup.command(name='create', description='Adds task to specific board')
async def add_task(interaction:discord.Interaction, task:str, board:str):
    if not interaction.user.id in scanmembers:
        return await interaction.response.send_message('You are not part of the scanlation group and cannot use this command!')
    tasks = load_tasks()
    if board not in tasks:
        return await interaction.response.send_message(f'`That board does not exist. Use /createboard "Board" to create a board!`')
    tasks[board].append({'task': task, 'status': 'backlog', 'assigned': []})
    save_tasks(tasks)
    await interaction.response.send_message(f'Task "{task}" added to board "{board}"')
@add_task.autocomplete('board')
async def boardautoaddtask(interaction:discord.Interaction, current:str):
    tasks = load_tasks()
    boards = []
    for board in tasks:
        if not any(t['status'] == board for t in tasks[board]):
            boards.append(board)
    all_choices = [
        app_commands.Choice(name=name, value=name)
        for name in boards
    ]
    if not current:
        return all_choices
    return [
        ch for ch in all_choices
        if ch.name.lower().startswith((current.lower()))
    ] or all_choices

@taskgroup.command(name='remove', description='Removes tasks from specific board')
async def remove_task(interaction:discord.Interaction, task:str, board:str):
    if not interaction.user.id in scanmembers:
        return await interaction.response.send_message('You are not part of the scanlation group and cannot use this command!')
    tasks = load_tasks()
    if board in tasks:
        for t in tasks[board]:
            if t['task'] == task:
                tasks[board].remove(t)
                save_tasks(tasks)
                await interaction.response.send_message(f'Task "{task}" removed from board "{board}"')
                return
        await interaction.response.send_message(f'Task "{task}" not found on board "{board}"')
    else:
        await interaction.response.send_message('Invalid board name')
@remove_task.autocomplete('board')
async def boardautoremovetask(interaction:discord.Interaction, current:str):
    tasks = load_tasks()
    boards = []
    for board in tasks:
        if not any(t['status'] == board for t in tasks[board]):
            boards.append(board)
    all_choices = [
        app_commands.Choice(name=name, value=name)
        for name in boards
    ]
    if not current:
        return all_choices
    return [
        ch for ch in all_choices
        if ch.name.lower().startswith((current.lower()))
    ] or all_choices

@taskgroup.command(name='updatestatus', description='Changes task status from specific board into user-defined status')
async def move_task(interaction:discord.Interaction, board:str, task:str, status:str):
    if not interaction.user.id in scanmembers:
        return await interaction.response.send_message('You are not part of the scanlation group and cannot use this command!')
    task, src_board, dest_board = task, board, status
    tasks = load_tasks()
    task_found = False
    for t in tasks[src_board]:
        if t['task'] == task:
            t['status'] = dest_board
            save_tasks(tasks)
            await interaction.response.send_message(f'Task "{task}" status changed to "{dest_board}" on board "{src_board}".')
            task_found = True
            break
    if not task_found:
        await interaction.response.send_message(f'Task "{task}" not found on board "{src_board}"')
@move_task.autocomplete('board')
async def boardautomovetask(interaction:discord.Interaction, current:str):
    tasks = load_tasks()
    boards = []
    for board in tasks:
        if not any(t['status'] == board for t in tasks[board]):
            boards.append(board)
    all_choices = [
        app_commands.Choice(name=name, value=name)
        for name in boards
    ]
    if not current:
        return all_choices
    return [
        ch for ch in all_choices
        if ch.name.lower().startswith((current.lower()))
    ] or all_choices

@bot.tree.command(name='delboard', description='Deletes a board.')
async def delb(interaction:discord.Interaction, board:str):
    if not interaction.user.id in scanmembers:
        return await interaction.response.send_message('You are not part of the scanlation group and cannot use this command!')
    tasks = load_tasks()
    if board not in tasks:
        return await interaction.response.send_message(f"`That board doesn't exist!`")
    await interaction.response.send_message(f'`Are you sure you wish to delete the "{board}" board? You will lose {len(tasks[board])} tasks!`' + '\n' + '**Reply with Y to continue:**')
    msg = await bot.wait_for('message', check = lambda x: x.channel.id == interaction.channel.id and interaction.user.id == x.author.id)
    if msg.content.lower() == 'y':
        del tasks[board]
        save_tasks(tasks)
        await interaction.response.send_message(f'`{board} has been deleted!`')
    else:
        await interaction.response.send_message(f'`Board deletion canceled.`')
@delb.autocomplete('board')
async def boardautodelb(interaction:discord.Interaction, current:str):
    tasks = load_tasks()
    boards = []
    for board in tasks:
        if not any(t['status'] == board for t in tasks[board]):
            boards.append(board)
    all_choices = [
        app_commands.Choice(name=name, value=name)
        for name in boards
    ]
    if not current:
        return all_choices
    return [
        ch for ch in all_choices
        if ch.name.lower().startswith((current.lower()))
    ] or all_choices

@bot.tree.command(name='createboard', description='Creates a board.')
async def cb(interaction:discord.Interaction, board:str):
    if not interaction.user.id in scanmembers:
        return await interaction.response.send_message('You are not part of the scanlation group and cannot use this command!')
    tasks = load_tasks()
    if board in tasks:
        return await interaction.response.send_message(f'`That board already exists!`')
    tasks[board] = []
    save_tasks(tasks)
    await interaction.response.send_message(f'`{board} has been created!`')

@bot.tree.command(name='list', description= 'Lists all tasks in a specific board')
async def list_tasks(interaction:discord.Interaction, board:str):
    tasks = load_tasks()
    if board in tasks:
        if tasks[board]:
            msg = f'***{board}* Board:**\n'
            for i, t in enumerate(tasks[board]):
                assign = t['assigned']
                assigned = ['*Assigned Users:*']
                for user in assign:
                    aaaa = (await bot.fetch_user(user[0]))
                    assigned.append(f'`{aaaa.name}#{aaaa.discriminator}` - `{user[1]}`')
                assigned = ('\n'.join(assigned)).strip()
                if assigned == '*Assigned Users:*':
                    assigned = '*Assigned Users:*\nNobody'
                msg += f'{i+1}. *{t["task"]}* - {t["status"].capitalize()}\n{assigned}\n'
            await interaction.response.send_message(msg)
        else:
            await interaction.response.send_message(f'`The "{board}" board is empty.`')
    else:
        await interaction.response.send_message(f'`The "{board}" board does not exist.`')
@list_tasks.autocomplete('board')
async def boardautolisttask(interaction:discord.Interaction, current:str):
    tasks = load_tasks()
    boards = []
    for board in tasks:
        if not any(t['status'] == board for t in tasks[board]):
            boards.append(board)
    all_choices = [
        app_commands.Choice(name=name, value=name)
        for name in boards
    ]
    if not current:
        return all_choices
    return [
        ch for ch in all_choices
        if ch.name.lower().startswith((current.lower()))
    ] or all_choices

@bot.tree.command(name='boards', description='Display all boards and available statuses')
async def list_boards(interaction:discord.Interaction):
    tasks = load_tasks()
    boards = [board for board in tasks if not any(t.get('status') == board for t in tasks.get(board, []))]
    if boards:
        message = f'Available boards:\n- {sorted(boards)}'
    else:
        message = '`No boards found. Use /createboard "Board" to create a board!`'
    await interaction.response.send_message(message)

@bot.tree.command(name='help', description='Shows a help message.')
async def help(interaction:discord.Interaction):
    global prefix
    text_commands = [f'{command.name}* - {command.description}' for command in bot.commands]
    slash_commands = [f'{command.qualified_name}* - {command.description}' for command in bot.tree.get_commands() if not hasattr(command, 'commands')]
    group_commands = [command for command in bot.tree.get_commands() if hasattr(command, 'commands')]
    embed = discord.Embed(
        title='Help',
        description='\n'.join([f'*{prefix}{line}' for line in text_commands + slash_commands]),
        color=discord.Color.green()
    )
    for command in group_commands:
        subcommands = [f'*/{cmd.qualified_name}* - {cmd.description}' for cmd in command.commands]
        embed.add_field(name=command.name.capitalize(), value='\n'.join(subcommands), inline=False)
    await interaction.response.send_message(embed=embed)

# Text commands
@bot.command(name='sync', description='Syncs the command tree (slash commmands) for the bot!')
async def sync(ctx:commands.Context):
    if ctx.author.id in botowners:
        await bot.tree.sync()
        embed = discord.Embed(
            title='Sync Successful.',
            color = discord.Color.green(),
            description='The sync may take some time to update. If this is your first time doing it, it may take up to 1 minute!'
        )
        await ctx.reply(embed=embed)
    else:
        await ctx.reply('Invalid permissions. You must be a bot owner to do this!') 

@bot.command(name='updatelist', description='Force updates group lists. Only use this when adding users directly to the config')
async def sync(ctx:commands.Context):
    global botowners, scanowners, scanmembers
    botowners = read_file('configs/botowners.txt')
    scanowners = read_file('configs/scanowners.txt')
    scanmembers = read_file('configs/scanmembers.txt')
    embed = discord.Embed(
            title='Group lists updated',
            color = discord.Color.green(),
            description = 'Group lists have been forcefully updated'
    )
    await ctx.reply(embed= embed)


# add groups
bot.tree.add_command(groupgroup)
bot.tree.add_command(taskgroup)

# events
@bot.event
async def on_ready():
    print('Ready')

# error handling
@bot.event
async def on_command_error(ctx:commands.Context, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        # we don't want it to send something every time a message starts with !
        pass
    else:
        await ctx.reply('Something went wrong!')
        print(''.join(traceback.format_exception(error, error, error.__traceback__)))

@bot.event
async def on_error(*args):
    print(args)

# start bot
print(botowners)
bot.run(TOKEN)