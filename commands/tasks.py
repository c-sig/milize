from discord import app_commands
from config import *
import os
import yaml

taskgroup = app_commands.Group(name='task', description='Task commands.')

def load_database():
    with open('configs/database.yaml', 'r') as file:
        database = yaml.safe_load(file)
    return database

def autocomplete(choices: list, current: str):
    if not current:
        return choices
    return [ch for ch in choices if ch.name.lower().startswith(current.lower())] or choices

def loadboards():
    with open('configs/database.yaml', 'r') as file:
        boards = yaml.safe_load(file)
    return boards

def get_user_id_for_task(taskname, boardname):
    # load the database
    database = load_database()

    # check if the board exists
    if boardname not in database:
        print(f'Board {boardname} does not exist.')
        return None

    # check if the task exists in the board
    if taskname not in database[boardname]:
        print(f'Task {taskname} does not exist in board {boardname}.')
        return None

    # get the user ID associated with the task
    user_id = None
    for key, value in database[boardname][taskname].items():
        if value:
            user_id = key
            break

    return user_id

@taskgroup.command(name='create', description='Creates a task.')
async def create_task(interaction: discord.Interaction, taskname: str, boardname: str):
    if not os.path.exists('configs'):
        os.mkdir('configs')

    if not os.path.exists('configs/database.yaml'):
        with open('configs/database.yaml', 'w') as file:
            yaml.dump({boardname: {}}, file)
        await interaction.response.send_message(f'Created new database file.')

    database = load_database()

    if boardname in database:
        database[boardname][taskname] = {}
        with open('configs/database.yaml', 'w') as file:
            yaml.dump(database, file)
        await interaction.response.send_message(f'Added task {taskname} to board {boardname}')

    else:
        database[boardname] = {taskname: {}}
        with open('configs/database.yaml', 'w') as file:
            yaml.dump(database, file)
        await interaction.response.send_message(f'Created new board {boardname} with task {taskname}')

@create_task.autocomplete('boardname')
async def createautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@taskgroup.command(name='delete', description='Deletes a task.')
async def delete_task(interaction: discord.Interaction, taskname: str, boardname: str):
    if not os.path.exists('configs'):
        await interaction.response.send_message('No database found.')
        return

    if not os.path.exists('configs/database.yaml'):
        await interaction.response.send_message('No database found.')
        return

    database = load_database()

    if boardname not in database:
        await interaction.response.send_message(f'{boardname} does not exist.')
        return

    if taskname not in database[boardname]:
        await interaction.response.send_message(f'Task {taskname} does not exist in board {boardname}.')
        return

    del database[boardname][taskname]
    with open('configs/database.yaml', 'w') as file:
        yaml.dump(database, file)

    await interaction.response.send_message(f'Deleted task {taskname} from board {boardname}')

@delete_task.autocomplete('boardname')
async def deleteautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@taskgroup.command(name='assign', description='Assigns a manager to a task')
async def assign_task(interaction: discord.Interaction, taskname: str, boardname: str, userid: discord.Member):
    if not os.path.exists('configs'):
        await interaction.response.send_message('No database found.')
        return

    if not os.path.exists('configs/database.yaml'):
        database = {}
    else:
        with open('configs/database.yaml', 'r') as file:
            database = yaml.safe_load(file)
            if database is None:
                database = {}

    if boardname not in database:
        await interaction.response.send_message(f'Board {boardname} does not exist.')

    if taskname not in database[boardname]:
        await interaction.response.send_message(f'Task {taskname} does not exist in board {boardname}.')
        return

    # assign the user ID to the task
    database[boardname][taskname][userid.id] = True
    with open('configs/database.yaml', 'w') as file:
        yaml.dump(database, file)

    await interaction.response.send_message(f'Assigned user {userid} to task {taskname} in board {boardname}')

@assign_task.autocomplete('boardname')
async def assignautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@taskgroup.command(name='list', description='Lists available tasks in a board.')
async def list_tasks(interaction: discord.Interaction, boardname: str):
    if not os.path.exists('configs'):
        await interaction.response.send_message('No database found. Aborting task listing')
        return

    # check if database.yaml exists
    if not os.path.exists('configs/database.yaml'):
        await interaction.response.send_message('No database found. Aborting task listing')
        return

    # load the database
    with open('configs/database.yaml', 'r') as file:
        database = yaml.safe_load(file)
        if database is None:
            database = {}

    # check if the board exists
    if boardname not in database:
        await interaction.response.send_message(f'Board {boardname} does not exist.')
        return

    tasks = database[boardname]
    if len(tasks) == 0:
        await interaction.response.send_message(f'No tasks found in board {boardname}')
        return

    message = f'Tasks in board {boardname}:\n'
    for taskname, users in tasks.items():
        message += f'- {taskname}\n'
        if len(users) > 0:
            message += '  Assigned users:\n'
            for userid in users:
                assignees = await interaction.guild.fetch_member(int(userid))
                message += f'  - {assignees}\n'
        else:
            message += '  No users assigned\n'
    await interaction.response.send_message(message)

@list_tasks.autocomplete('boardname')
async def listautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@taskgroup.command(name='rename', description='Renames a task.')
async def rename_task(interaction: discord.Interaction, taskname: str, new_taskname: str, boardname: str):
    # check if configs folder exists
    if not os.path.exists('configs'):
        await interaction.response.send_message('No database found.')
        return

    # check if database.yaml exists
    if not os.path.exists('configs/database.yaml'):
        await interaction.response.send_message('No database found.')
        return

    # load the database
    with open('configs/database.yaml', 'r') as file:
        database = yaml.safe_load(file)
        if database is None:
            database = {}

    # check if the board exists
    if boardname not in database:
        await interaction.response.send_message(f'Board {boardname} does not exist.')
        return

    # check if the task exists
    if taskname not in database[boardname]:
        await interaction.response.send_message(f'Task {taskname} does not exist in board {boardname}.')
        return

    # rename the task
    database[boardname][new_taskname] = database[boardname].pop(taskname)

    # write the changes to the database
    with open('configs/database.yaml', 'w') as file:
        yaml.dump(database, file)

    await interaction.response.send_message(f'Task {taskname} has been renamed to {new_taskname} in board {boardname}.')

@rename_task.autocomplete('boardname')
async def renameautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices
