import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.all()
intents.members = True
intents.guild_messages = True
intents.dm_messages = True

client = commands.Bot(command_prefix='!', intents=intents)

#load json
def load_tasks():
    if os.path.exists('tasks.json'):
        with open('tasks.json', 'r') as f:
            return json.load(f)
    else:
        return {}

#save to json
def save_tasks(tasks):
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f, indent=4)

#add task to board
@client.command(name='add')
async def add_task(ctx, *, args):
    args_list = args.split('"')[1::2]  # split args by quotes
    if len(args_list) == 2:
        task, board = args_list[0], args_list[1]
        tasks = load_tasks()
        if board not in tasks:
            tasks[board] = []
        tasks[board].append({'task': task, 'status': 'backlog'})
        save_tasks(tasks)
        await ctx.send(f'Task "{task}" added to board "{board}"')
    else:
        await ctx.send('Invalid arguments')


#remove task from board
@client.command(name='remove')
async def remove_task(ctx, *, args):
    args_list = args.split('"')[1::2]  # split args by quotes
    if len(args_list) == 2:
        task, board = args_list
        tasks = load_tasks()
        if board in tasks:
            for t in tasks[board]:
                if t['task'] == task:
                    tasks[board].remove(t)
                    save_tasks(tasks)
                    await ctx.send(f'Task "{task}" removed from board "{board}"')
                    return
            await ctx.send(f'Task "{task}" not found on board "{board}"')
        else:
            await ctx.send('Invalid board name')
    else:
        await ctx.send('Invalid arguments')

#list tasks for board
@client.command(name='list')
async def list_tasks(ctx, board):
    tasks = load_tasks()
    if board in tasks:
        if tasks[board]:
            msg = f'**{board.capitalize()} Board:**\n'
            for i, t in enumerate(tasks[board]):
                msg += f'{i+1}. {t["task"]} - {t["status"].capitalize()}\n'
            await ctx.send(msg)
        else:
            await ctx.send(f'The "{board}" board is empty')
    else:
        await ctx.send(f'The "{board}" board does not exist')

@client.command(name='boards')
async def list_boards(ctx):
    tasks = load_tasks()
    boards = []
    for board in tasks:
        if not any(t['status'] == board for t in tasks[board]):
            boards.append(board)
    if boards:
        message = 'Available boards:\n- ' + '\n- '.join(sorted(boards))
    else:
        message = 'No boards found'
    await ctx.send(message)

#move tasks on board
@client.command(name='status')
async def move_task(ctx, *, args):
    args_list = args.split('"')[1::2]  # split args by quotes
    if len(args_list) == 3:
        task, src_board, dest_board = args_list
        tasks = load_tasks()
        if src_board not in tasks:
            tasks[src_board] = []
        if dest_board not in tasks:
            tasks[dest_board] = []
        task_found = False
        for t in tasks[src_board]:
            if t['task'] == task:
                t['status'] = dest_board
                save_tasks(tasks)
                await ctx.send(f'Task "{task}" moved to "{dest_board}" on board "{src_board}"')
                task_found = True
                break
        if not task_found:
            await ctx.send(f'Task "{task}" not found on board "{src_board}"')
    else:
        await ctx.send('Invalid arguments')

#error handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send('Invalid command')

client.run('TOKEN')

