import yaml
from discord import app_commands
from config import *

boardgroup = app_commands.Group(name='board', description='Board commands.')
CONFIGS_FOLDER = 'configs'
database_path = os.path.join(CONFIGS_FOLDER, 'database.yaml')
owners, managers, members, *_ = initializebot()
group_configs = {
    'owners': 'owner_id',
    'managers': 'manager_id',
    'members': 'member_id',
}


def update_config():
    group_configs = {
        'owners': 'owner_id',
        'managers': 'manager_id',
        'members': 'member_id',
    }
    owners_config = config.get('settings', group_configs['owners'])
    owners_ids = [id.strip() for id in owners_config.split(',')]
    managers_config = config.get('settings', group_configs['managers'])
    managers_ids = [id.strip() for id in managers_config.split(',')]
    members_config = config.get('settings', group_configs['members'])
    members_ids = [id.strip() for id in members_config.split(',')]

    # Update the global variables used in your code
    global owners, managers, members
    owners = [int(id) for id in owners_ids]
    managers = [int(id) for id in managers_ids]
    members = [int(id) for id in members_ids]


def check_permissions(user_id, allowed_groups):
    update_config()
    for group in allowed_groups:
        group_config = config.get('settings', group_configs[group])
        group_ids = [id.strip() for id in group_config.split(',')]
        if str(user_id) in group_ids:
            return True
    return False


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
    allowed_groups = ['owners', 'managers']
    if not check_permissions(interaction.user.id, allowed_groups):
        await interaction.response.send_message(f'You do not have the necessary permissions for this command')
        return
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
    allowed_groups = ['owners', 'managers']
    if not check_permissions(interaction.user.id, allowed_groups):
        await interaction.response.send_message(f'You do not have the necessary permissions for this command')
        return
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
    allowed_groups = ['owners', 'managers']
    if not check_permissions(interaction.user.id, allowed_groups):
        await interaction.response.send_message(f'You do not have the necessary permissions for this command')
        return
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
    allowed_groups = ['owners', 'managers']
    if not check_permissions(interaction.user.id, allowed_groups):
        await interaction.response.send_message(f'You do not have the necessary permissions for this command')
        return
    # Load board list from database
    boards = loadboards()

    # Output list
    list_contents = "The following boards are available:\n"
    for board in boards:
        list_contents += f"- {board}\n"

    await interaction.response.send_message(list_contents)
