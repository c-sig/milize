from discord import app_commands
from config import *
import discord
import yaml
from configparser import ConfigParser

permissiongroup = app_commands.Group(name='permission', description='Permission commands.')


def autocomplete(choices: list, current: str):
    if not current:
        return choices
    return [ch for ch in choices if ch.name.lower().startswith(current.lower())] or choices


@permissiongroup.command(name="add", description='Adds a user to a permission group.')
async def add_permission(interaction: discord.Interaction, user: discord.Member, group: str):
    owners, managers, members, *_ = initializebot()
    group_configs = {
        'owners': 'owner_id',
        'managers': 'manager_id',
        'members': 'member_id',
    }

    owners_config = config.get('settings', group_configs['owners'])
    owners_ids = [id.strip() for id in owners_config.split(',')]
    if str(interaction.user.id) not in owners_ids:
        await interaction.response.send_message(f'You are not authorized to perform this command.')
        return

    if group not in group_configs:
        await interaction.response.send_message(f'{group} is not a valid permission group!')
        return

    current = config.get('settings', group_configs[group])
    current_ids = [id.strip() for id in current.split(',')]
    if str(user.id) in current_ids:
        await interaction.response.send_message(f'{user} is already in permission group {group}!')
        return

    # handle the case of an empty configuration value separately
    if not current:
        new_ids = [str(user.id)]
    else:
        new_ids = [id.strip() for id in current.split(',') if id.strip() != ''] + [str(user.id)]
    config.set('settings', group_configs[group], ', '.join(new_ids))

    try:
        with open(config_file, 'w') as configfile:
            config.write(configfile)
    except IOError as e:
        await interaction.response.send_message(f'Error writing to configuration file: {str(e)}')
        return

    await interaction.response.send_message(f'{user} has been added to permission group {group}!')


@add_permission.autocomplete('group')
async def addautocomplete(interaction: discord, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in ['owners', 'managers', 'members']]
    return autocomplete(choices, current)


@permissiongroup.command(name="remove", description='Removes a user from a permission group.')
async def remove_permission(interaction: discord.Interaction, user: discord.Member, group: str):
    owners, managers, members, *_ = initializebot()
    group_configs = {
        'owners': 'owner_id',
        'managers': 'manager_id',
        'members': 'member_id',
    }

    owners_config = config.get('settings', group_configs['owners'])
    owners_ids = [id.strip() for id in owners_config.split(',')]
    if str(interaction.user.id) not in owners_ids:
        await interaction.response.send_message(f'You are not authorized to perform this command.')
        return

    if group not in group_configs:
        await interaction.response.send_message(f'{group} is not a valid permission group!')
        return

    current = config.get('settings', group_configs[group])
    current_ids = [id.strip() for id in current.split(',')]
    if str(user.id) not in current_ids:
        await interaction.response.send_message(f'{user} is not in permission group {group}!')
        return
    new_ids = [id.strip() for id in current.split(',') if id.strip() != str(user.id)]
    config.set('settings', group_configs[group], ', '.join(new_ids))

    try:
        with open(config_file, 'w') as configfile:
            config.write(configfile)
    except IOError as e:
        await interaction.response.send_message(f'Error writing to configuration file: {str(e)}')
        return

    await interaction.response.send_message(f'{user} has been removed from permission group {group}!')


@remove_permission.autocomplete('group')
async def removeautocomplete(interaction: discord, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in ['owners', 'managers', 'members']]
    return autocomplete(choices, current)


@permissiongroup.command(name="list", description='Lists the users in a permission group.')
async def list_permission(interaction: discord.Interaction, group: str):
    owners, managers, members, *_ = initializebot()
    group_configs = {
        'owners': 'owner_id',
        'managers': 'manager_id',
        'members': 'member_id',
    }

    owners_config = config.get('settings', group_configs['owners'])
    owners_ids = [id.strip() for id in owners_config.split(',')]
    if str(interaction.user.id) not in owners_ids:
        await interaction.response.send_message(f'You are not authorized to perform this command.')
        return

    if group not in group_configs:
        await interaction.response.send_message(f'{group} is not a valid permission group!')
        return

    current = config.get('settings', group_configs[group])
    current_ids = [id.strip() for id in current.split(',') if id.strip() != '']
    if not current_ids:
        await interaction.response.send_message(f'No users found in permission group {group}!')
        return

    member_list = []
    for id in current_ids:
        try:
            member = await interaction.guild.fetch_member(int(id))
            member_list.append(member.display_name)
        except discord.errors.NotFound:
            pass

    if not member_list:
        await interaction.response.send_message(f'No valid users found in permission group {group}!')
        return

    member_list_str = '\n'.join(member_list)
    await interaction.response.send_message(f'Users in {group}:\n{member_list_str}')


@list_permission.autocomplete('group')
async def listautocomplete(interaction: discord, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in ['owners', 'managers', 'members']]
    return autocomplete(choices, current)  # permissiongroup
