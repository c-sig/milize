import yaml
from discord import app_commands
from config import *

boardgroup = app_commands.Group(name='board', description='Board commands.')
CONFIGS_FOLDER = 'configs'
database_path = os.path.join(CONFIGS_FOLDER, 'database.yaml')

def loadboards():
    with open(database_path, 'r') as file:
        boards = yaml.safe_load(file)
    return boards

def autocomplete(choices: list, current: str):
    if not current:
        return choices
    return [ch for ch in choices if ch.name.lower().startswith(current.lower())] or choices

@boardgroup.command(name='create', description='Creates a board.')
async def create_board(interaction: discord.Interaction, boardname: str):
    # Load board list from database
    if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
        boards = loadboards()
    else:
        boards = {}

    # Check if board exists
    if boardname in boards:
        await interaction.response.send_message(f'{boardname} already exists.')
        return

    # Add board to list and save changes to database
    boards[boardname] = {}
    with open(database_path, 'w') as file:
        yaml.dump(boards, file)

    await interaction.response.send_message(f'{boardname} has been created.')

@boardgroup.command(name='delete', description='Deletes an existing board')
async def delete_board(interaction: discord.Interaction, boardname: str):
    # Load board list from database
    boards = loadboards()

    # Check if board exists
    if boardname not in boards:
        await interaction.response.send_message(f'{boardname} does not exist.')
        return

    # Delete board from list and save changes to database
    del boards[boardname]
    with open(database_path, 'w') as file:
        yaml.dump(boards, file)

    await interaction.response.send_message(f'{boardname} has been deleted.')

@delete_board.autocomplete('boardname')
async def deleteautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@boardgroup.command(name='rename', description='Renames an existing board')
async def rename_board(interaction: discord.Interaction, oldname: str, newname: str):
    # Load board list from database
    boards = loadboards()

    # Check if old board exists
    if oldname not in boards:
        await interaction.response.send_message(f'{oldname} does not exist.')
        return

    # Check if new name already taken
    if newname in boards:
        await interaction.response.send_message(f'{oldname} already exists.')
        return

    # Rename board and save changes to database
    boards[newname] = boards[oldname]
    del boards[oldname]
    with open(database_path, 'w') as file:
        yaml.dump(boards, file)

    await interaction.response.send_message(f'{oldname} has been renamed to {newname}.')

@rename_board.autocomplete('oldname')
async def renameautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@boardgroup.command(name='list', description='Lists all available boards')
async def list_board(interaction: discord.Interaction):
    # Load board list from database
    boards = loadboards()

    # Output list
    list_contents = "The following boards are available:\n"
    for board in boards:
        list_contents += f"- {board}\n"

    await interaction.response.send_message(list_contents)
