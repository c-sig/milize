import discord
import yaml
from discord import app_commands
from config import *

jobgroup = app_commands.Group(name='job', description='Job commands')
CONFIGS_FOLDER = 'configs'
database_path = os.path.join(CONFIGS_FOLDER, 'database.yaml')

jobtypes = ['Translator', ' Proofreader', ' Typesetter', ' Cleaner', ' Redrawer', ' Quality Checker']


def loaddatabase():
    with open(database_path) as f:
        data = yaml.safe_load(f)
    return data


def loadboards():
    with open(database_path, 'r') as file:
        boards = yaml.safe_load(file)
    return boards


def autocomplete(choices: list, current: str):
    if not current:
        return choices
    return [ch for ch in choices if ch.name.lower().startswith(current.lower())] or choices


@jobgroup.command(name='claim', description='Claim a job.')
async def claim_job(interaction: discord.Interaction, boardname: str, taskname: str, jobtype: str):
    data = loaddatabase()
    if boardname not in data:
        await interaction.response.send_message(f"Board '{boardname}' not found")
    if taskname not in data[boardname]:
        await interaction.response.send_message(f"Task '{taskname}' not found in board '{boardname}'")

    # Check if the job already exists
    jobs_dict = data[boardname][taskname].get('jobs', {})
    if jobtype in jobs_dict:
        # Job already exists, update the assigned user
        assigned_user_id = interaction.user.id
        assigned_user = await interaction.guild.fetch_member(assigned_user_id)
        jobs_dict[jobtype]['user_assigned'] = assigned_user_id
    else:
        await interaction.response.send_message(f"Job not available. Contact your project manager.")

    data[boardname][taskname]['jobs'] = jobs_dict

    # Save the updated YAML file
    with open('configs/database.yaml', 'w') as f:
        yaml.safe_dump(data, f)

    await interaction.response.send_message(
        f'{assigned_user.name} assigned to do {jobtype} in {taskname}, {boardname}.')


@claim_job.autocomplete('boardname')
async def claimboardautocomplete(interaction: discord.Interaction, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@claim_job.autocomplete('jobtype')
async def claimjobautocomplete(interaction: discord.Interaction, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@jobgroup.command(name='unclaim', description='Unclaims a job')
async def unclaim_job(interaction: discord.Interaction, boardname: str, taskname: str, jobtype: str):
    data = loaddatabase()
    if boardname not in data:
        await interaction.response.send_message(f"Board '{boardname}' not found")
    elif taskname not in data[boardname]:
        await interaction.response.send_message(f"Task '{taskname}' not found in board '{boardname}'")
    elif jobtype not in data[boardname][taskname].get('jobs', {}):
        await interaction.response.send_message(
            f"Job '{jobtype}' not found in task '{taskname}' of board '{boardname}'")
    elif data[boardname][taskname]['jobs'][jobtype].get('user_assigned') != interaction.user.id:
        await interaction.response.send_message(
            f"You are not assigned to do job '{jobtype}' in task '{taskname}' of board '{boardname}'")
    else:
        data[boardname][taskname]['jobs'][jobtype].pop('user_assigned', None)
        with open('configs/database.yaml', 'w') as f:
            yaml.safe_dump(data, f)
        await interaction.response.send_message(
            f"You have successfully unclaimed job '{jobtype}' in task '{taskname}' of board '{boardname}'")


@unclaim_job.autocomplete('boardname')
async def unclaimboardautocomplete(interaction: discord.Interaction, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@unclaim_job.autocomplete('jobtype')
async def unclaimjobautocomplete(interaction: discord.Interaction, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@jobgroup.command(name='unassign', description='Unassigns a user from a job.')
async def unassign_job(interaction: discord.Interaction, boardname: str, taskname: str, jobtype: str):
    data = loaddatabase()

    # Check if the board and task exist
    if boardname not in data:
        await interaction.response.send_message(f"Board '{boardname}' not found")
        return
    if taskname not in data[boardname]:
        await interaction.response.send_message(f"Task '{taskname}' not found in board '{boardname}'")
        return

    # Check if the job exists
    jobs_dict = data[boardname][taskname].get('jobs', {})
    if jobtype not in jobs_dict:
        await interaction.response.send_message(f"Job '{jobtype}' not found in task '{taskname}'")
        return

    # Check if the job already has no assigned user
    if 'user_assigned' not in jobs_dict[jobtype]:
        await interaction.response.send_message(f"Job '{jobtype}' in '{taskname}' already has no assigned user")
        return

    # Remove the user_assigned field from the job
    del jobs_dict[jobtype]['user_assigned']
    del jobs_dict[jobtype]['status']
    data[boardname][taskname]['jobs'] = jobs_dict

    # Save the updated YAML file
    with open('configs/database.yaml', 'w') as f:
        yaml.safe_dump(data, f)

    await interaction.response.send_message(
        f'{jobtype} in {taskname}, {boardname} unassigned from its user.')


@unassign_job.autocomplete('boardname')
async def unassignboardautocomplete(interaction: discord.Interaction, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@unassign_job.autocomplete('jobtype')
async def unassignjobautocomplete(interaction: discord.Interaction, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@jobgroup.command(name='create', description='Creates a job.')
async def create_job(interaction: discord.Interaction, boardname: str, taskname: str, jobtype: str):
    data = loaddatabase()

    # Check if the board and task exist
    if boardname not in data:
        raise ValueError(f"Board '{boardname}' not found")
    if taskname not in data[boardname]:
        raise ValueError(f"Task '{taskname}' not found in board '{boardname}'")

    # Add the job to the task with the given status
    jobs_dict = data[boardname][taskname].get('jobs', {})
    jobs_dict[jobtype] = {'status': 'Backlog'}
    data[boardname][taskname]['jobs'] = jobs_dict

    # Save the updated YAML file
    with open('configs/database.yaml', 'w') as f:
        yaml.safe_dump(data, f)

    await interaction.response.send_message(f'{jobtype} created in {taskname}, {boardname}.')


@create_job.autocomplete('boardname')
async def createboardautocomplete(interaction: discord.Interaction, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@create_job.autocomplete('jobtype')
async def createjobautocomplete(interaction: discord.Interaction, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@jobgroup.command(name='assign', description='Assigns a user to a job.')
async def assign_job(interaction: discord.Interaction, boardname: str, taskname: str, jobtype: str,
                     user_assigned: discord.Member):
    data = loaddatabase()

    # Check if the board and task exist
    if boardname not in data:
        await interaction.response.send_message(f"Board '{boardname}' not found")
    if taskname not in data[boardname]:
        await interaction.response.send_message(f"Task '{taskname}' not found in board '{boardname}'")

    # Check if the job already exists
    jobs_dict = data[boardname][taskname].get('jobs', {})
    if jobtype in jobs_dict:
        # Job already exists, update the assigned user
        jobs_dict[jobtype]['user_assigned'] = user_assigned.id
    else:
        # Job does not exist, create a new job with the assigned user and backlog status
        jobs_dict[jobtype] = {'user_assigned': user_assigned.id, 'status': 'Backlog'}

    data[boardname][taskname]['jobs'] = jobs_dict

    # Save the updated YAML file
    with open('configs/database.yaml', 'w') as f:
        yaml.safe_dump(data, f)

    await interaction.response.send_message(
        f'{user_assigned.name} assigned to do {jobtype} in {taskname}, {boardname}.')


@assign_job.autocomplete('boardname')
async def assignboardautocomplete(interaction: discord.Interaction, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@assign_job.autocomplete('jobtype')
async def assignjobautocomplete(interaction: discord.Interaction, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@jobgroup.command(name='update', description='Updates job status.')
async def update_job(interaction: discord.Interaction, boardname: str, taskname: str, jobtype: str, status: str):
    data = loaddatabase()

    # Check if the board and task exist
    if boardname not in data:
        await interaction.response.send_message(f"Board '{boardname}' not found")
    if taskname not in data[boardname]:
        await interaction.response.send_message(f"Task '{taskname}' not found in board '{boardname}'")

    # Check if the job exists in the task
    jobs_dict = data[boardname][taskname].get('jobs', {})
    if jobtype not in jobs_dict:
        await interaction.response.send_message(f"Job '{jobtype}' not found in task '{taskname}'")

    # Update the status of the job
    jobs_dict[jobtype]['status'] = status
    data[boardname][taskname]['jobs'] = jobs_dict

    # Save the updated YAML file
    with open('configs/database.yaml', 'w') as f:
        yaml.safe_dump(data, f)

    await interaction.response.send_message(f'{jobtype} for {taskname} in {boardname} updated to {status}')


@update_job.autocomplete('boardname')
async def updateboardautocomplete(interaction: discord.Interaction, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@update_job.autocomplete('status')
async def updatestatusautocomplete(interaction: discord.Interaction, current: str):
    status = ['Backlog', 'Working', 'Completed']
    choices = [app_commands.Choice(name=name, value=name) for name in status]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@update_job.autocomplete('jobtype')
async def updatejobautocomplete(interaction: discord.Interaction, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices


@jobgroup.command(name='list', description='Lists all jobs in a task.')
async def list_job(interaction: discord.Interaction, boardname: str, taskname: str):
    data = loaddatabase()

    # Check if the board and task exist
    if boardname not in data:
        await interaction.response.send_message(f"Board '{boardname}' not found")
    if taskname not in data[boardname]:
        await interaction.response.send_message(f"Task '{taskname}' not found in board '{boardname}'")

    # List all jobs in the task with assigned users and statuses
    jobs_dict = data[boardname][taskname].get('jobs', {})
    message = ""
    if jobs_dict:
        for jobtype, jobinfo in jobs_dict.items():
            user_assigned = jobinfo.get('user_assigned')
            user_assigned = interaction.guild.get_member(int(user_assigned)) if user_assigned else "Not assigned"
            status = jobinfo.get('status', 'No status')
            message += f"{jobtype}: {user_assigned} ({status})\n"
    else:
        message = "No jobs found in this task."

    await interaction.response.send_message(message)


@list_job.autocomplete('boardname')
async def listautocomplete(interaction: discord.Interaction, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices
