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

@jobgroup.command(name='create', description='Creates a job.')
async def create_job(interaction: discord, boardname: str, taskname: str, jobtype: str):
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
async def createboardautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@create_job.autocomplete('jobtype')
async def createjobautocomplete(interaction: discord, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice.name for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@jobgroup.command(name='assign', description='Assigns a user to a job.')
async def assign_job(interaction: discord, boardname: str, taskname: str, jobtype: str, user_assigned: discord.Member):
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

    await interaction.response.send_message(f'{user_assigned.name} assigned to do {jobtype} in {taskname}, {boardname}.')

@assign_job.autocomplete('boardname')
async def assignboardautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@assign_job.autocomplete('jobtype')
async def assignjobautocomplete(interaction: discord, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice.name for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@jobgroup.command(name='update', description='Updates job status.')
async def update_job(interaction: discord, boardname: str, taskname: str, jobtype: str, status: str):
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
async def updateboardautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@update_job.autocomplete('status')
async def updatestatusautocomplete(interaction: discord, current: str):
    status = ['Backlog', 'Working', 'Completed']
    choices = [app_commands.Choice(name=name, value=name) for name in status]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@update_job.autocomplete('jobtype')
async def updatejobautocomplete(interaction: discord, current: str):
    choices = [app_commands.Choice(name=name, value=name) for name in jobtypes]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

@jobgroup.command(name='list', description='Lists all jobs in a task.')
async def list_job(interaction: discord, boardname: str, taskname: str):
    data = loaddatabase()

    # Check if the board and task exist
    if boardname not in data:
        await interaction.response.send_message(f"Board '{boardname}' not found")
    if taskname not in data[boardname]:
        await interaction.response.send_message(f"Task '{taskname}' not found in board '{boardname}'")

    # List all jobs in the task with assigned users and statuses
    jobs_dict = data[boardname][taskname].get('jobs', {})
    message = ""
    for jobtype, jobinfo in jobs_dict.items():
        user_assigned = jobinfo['user_assigned']
        user_assigned = interaction.guild.get_member(int(user_assigned))
        status = jobinfo['status']
        message += f"{jobtype}: {user_assigned} ({status})\n"

    await interaction.response.send_message(message)

@list_job.autocomplete('boardname')
async def listautocomplete(interaction: discord, current: str):
    boards = loadboards()
    choices = [app_commands.Choice(name=name, value=name) for name in boards.keys()]
    filtered_choices = [choice for choice in choices if choice.name.startswith(current)]
    return filtered_choices

