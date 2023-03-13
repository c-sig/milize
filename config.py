import os
import discord
import configparser
from discord.ext import commands

config_file = "configs/config.ini"
config = configparser.ConfigParser()


def initializebot():
    if not os.path.exists("configs/"):
        os.mkdir("configs")

    if not os.path.exists(config_file):
        print("Configuration file not found. Please enter the following values:")
        bot_prefix = input("Prefix: ")
        scan_group_name = input("Group name: ")
        bot_token = input("Discord Bot Token: ")
        application_id = input("Application ID: ")
        owner_id = input("Input your User ID (or other bot owners separated by comma): ")
        manager_id = input("Input your project managers' IDs (separated by comma): ")
        member_id = input("Input your group members' IDs (separated by comma): ")

        owner_id = [id.strip() for id in owner_id.split(",")]
        manager_id = [id.strip() for id in manager_id.split(",")]
        member_id = [id.strip() for id in member_id.split(",")]

        config['settings'] = {
            'prefix': bot_prefix,
            'group_name': scan_group_name,
            'token': bot_token,
            'app_id': application_id,
            'owner_id': ','.join(owner_id),
            'manager_id': ','.join(manager_id),
            'member_id': ','.join(member_id)
        }
        with open(config_file, 'w') as f:
            config.write(f)
    else:
        config.read(config_file)

    prefix = config.get('settings', 'prefix')
    group_name = config.get('settings', 'group_name')
    token = config.get('settings', 'token')
    app_id = config.get('settings', 'app_id')
    owners = config.get('settings', 'owner_id').split(",")
    managers = config.get('settings', 'manager_id').split(",")
    members = config.get('settings', 'member_id').split(",")

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), intents=intents, id=app_id, help_command=None)
    return prefix, config_file, config, bot, group_name, token, owners, managers, members


def readpermissions():
    owners = config.get('settings', 'owner_id').split(",")
    managers = config.get('settings', 'manager_id').split(",")
    members = config.get('settings', 'member_id').split(",")

    return owners, managers, members
